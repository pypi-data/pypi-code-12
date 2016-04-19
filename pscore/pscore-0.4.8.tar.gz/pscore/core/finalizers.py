from datetime import time
import uuid

import os
from pscore.clients.saucelabs.saucelabs_client import SauceLabsClient
from pscore.config.test_configuration import TestConfiguration

REPORT_LINK_SCREENSHOT = 'Screenshot File'
REPORT_LINK_SG_TEST = 'Test Report'
REPORT_LINK_SG_SESSION = 'Session Report'
REPORT_LINK_SAUCELABS = 'Saucelabs Report'


class WebDriverFinalizer:
    def __init__(self):
        pass

    @staticmethod
    def create_screenshot_filename():
        return str(uuid.uuid4()) + '.png'

    @staticmethod
    def finalize(driver, test_failed, logger, test_context=None):
        """
        :type driver: selenium.webdriver.remote.webdriver.WebDriver
        """

        desired_execution_environment = TestConfiguration.get_execution_environment()
        using_skygrid = TestConfiguration.get_skygrid_enabled()

        if test_failed and TestConfiguration.get_html_dump_on_failure_enabled():
            logger.info("Test Finalizer: Dumping failing page HTML:\n" +
                        driver.page_source)
        try:
            final_url = driver.current_url
            logger.info('Test Finalizer: Final url: ' + final_url)
        except Exception as e:
            logger.error(
                'Test Finalizer: Exception thrown when attempting to get the drivers final url' + str(e))

        if desired_execution_environment == 'grid':
            if using_skygrid:
                WebDriverFinalizer.finalize_skygrid(driver, test_failed, test_context)
            else:
                WebDriverFinalizer.finalise_grid_driver(driver, test_failed, logger)

            return

        elif desired_execution_environment == 'local':
            WebDriverFinalizer.finalise_grid_driver(driver, test_failed, logger)

            return

        elif desired_execution_environment in ['saucelabs', 'sauce']:
            WebDriverFinalizer.finalise_saucelabs_driver(driver, test_failed, test_context)
            return

        else:
            logger.error(
                "Could not teardown driver properly as the specified execution environment was not recognised: %s "
                % desired_execution_environment)

        # Catch-all driver teardown.  This shouldn't be needed, but just in case something crazy happens we don't want
        # to leave any orphaned sessions open
        if driver is not None:
            logger.info(
                'Could not parse driver to finalize in any specific fashion.' +
                ' Quitting driver to prevent orphan session.')
            driver.quit()

        return

    @staticmethod
    def finalise_saucelabs_driver(driver, test_failed, test_context):
        test_context.logger.info('Finalizing driver for Saucelabs')
        try:
            job_id = driver.session_id
            test_context.logger.debug("Quitting driver instance.")
            driver.quit()

            test_context.logger.debug("Creating Saucelabs client.")
            client = SauceLabsClient(sauce_username=TestConfiguration.get_sauce_username(),
                                     sauce_access_key=TestConfiguration.get_sauce_key())

            test_context.logger.debug("Waiting for job to complete.")
            WebDriverFinalizer.wait_until_sauce_job_completes(client, job_id, test_context.logger)

            test_context.logger.debug("Setting job public.")
            client.set_job_public(job_id, True)

            if test_failed:
                test_context.logger.debug("Setting job pass status to False.")
                client.set_job_pass_status(job_id, False)
                error = test_context.error_message
                test_context.logger.debug("Setting job error text.")
                client.set_error(job_id, str(error))
            else:
                test_context.logger.debug("Setting job pass status to True.")
                client.set_job_pass_status(job_id, True)
        except TypeError as e:
            test_context.logger.error(
                "TypeError caught when finalizing for SauceLabs.  " +
                "This signifies a problem in the finalization code: %s" % str(
                    e))
            raise
        except Exception as e:
            test_context.logger.error("Exception caught when finalizing for SauceLabs: %s" % str(e))
            test_context.logger.debug("Waiting for job to complete.")
            raise
        finally:
            job_id = driver.session_id
            report_url = 'https://saucelabs.com/jobs/{}'.format(str(job_id))
            test_context.logger.info(
                "SauceLabs report: <a href=\"{}\" target=\"_blank\">{}</a>".format(report_url, REPORT_LINK_SAUCELABS))

    @staticmethod
    def wait_until_sauce_job_completes(client, job_id, logger):
        polling_delay_sec = 1
        max_attempts = 10
        job_completed = False

        for x in range(1, max_attempts):
            job_completed = client.job_is_complete(job_id)
            if job_completed:
                break

            else:

                time().sleep(polling_delay_sec)

        if not job_completed:
            logger.error("Saucelabs job %s did not complete within %s seconds during finalization"
                         % (job_id, str(max_attempts * polling_delay_sec)))

    @staticmethod
    def finalise_grid_driver(driver, test_failed, logger):
        if driver is not None:
            if test_failed:
                filename = WebDriverFinalizer.create_screenshot_filename()
                logger.info('Test Finalizer: Detected test failure, attempting screenshot: ' + filename)

                try:
                    file_path = os.path.join(TestConfiguration.get_screenshot_dir(), filename)
                    driver.save_screenshot(file_path)
                    screenshot_path = os.path.join(os.getcwd(), 'screenshots')
                    screenshot_dir = os.path.split(screenshot_path)[1] + "/" + filename
                    logger.info(
                        "Screenshot can be found here: <a href=\"{}\" target=\"_blank\">{}</a>".format(
                            screenshot_dir, REPORT_LINK_SCREENSHOT))
                except Exception as e:
                    logger.error('Test Finalizer: Exception thrown when attempting screenshot: ' + filename + str(e))

            else:
                logger.info('Test Finalizer: Detected test passed.')

            logger.info('Test Finalizer: Ending browser session.')
            driver.quit()

        else:
            logger.warning('Test Finalizer: Attempted to finalise test but the session had already terminated.')

    @staticmethod
    def finalize_skygrid(driver, test_failed, test_context):
        if driver is not None:
            if test_failed:
                WebDriverFinalizer.finalise_skygrid_driver_failure(driver, test_context)
            else:
                test_context.logger.info('Test Finalizer: Detected test passed.')
                driver.quit()
            test_context.logger.info('Test Finalizer: Ending browser session.')
        else:
            test_context.logger.warning(
                'Test Finalizer: Attempted to finalise test but the session had already terminated.')

    @staticmethod
    def finalise_skygrid_driver_failure(driver, test_context):
        from pscore.clients.skygrid.api.skygridapiclient import SkyGridApiClient as ApiClient, SkygridApiClientException
        from pscore.clients.skygrid.metadata.skygridmetadataclient import SkyGridMetaDataClient as ArtefactsClient
        from pscore.clients.skygrid.dao.data import TestData, Log
        import time as t

        skygrid_hub_node = driver.wrapped_driver.active_node_ip()
        session_id = driver.session_id
        caps = driver.desired_capabilities
        node_browser_version = caps['version']
        node_browser_type = caps['browserName']

        artefacts_client = ArtefactsClient(test_context.logger)
        grid_api_client = ApiClient(driver=driver)

        # upload screenshots taken by user
        try:
            artefacts_client.upload_screenshots(test_context.skygrid_screenshots)
        except Exception as e:
            test_context.logger.error(e)

        # upload final screenshot and kill driver
        try:
            screenshot = grid_api_client.take_screenshot()
            artefacts_client.upload_screenshot(screenshot.to_json())
        except Exception as e:
            test_context.logger.error(e)

        # MUST quit driver before uploading video, so video is finalized and ready to be copied
        driver.quit()

        # upload video
        try:
            video = grid_api_client.get_video()
            artefacts_client.upload_video(video.to_json())
        except Exception as e:
            test_context.logger.error(e)

        # upload test details
        with open('guid.txt') as f:
            guid = f.readline()

        test_session_guid = guid.strip()
        duration = int(t.time()) - test_context.start_time_seconds
        test_data = TestData(session_id, str(test_context.error_message), test_session_guid, test_context.test_name,
                             skygrid_hub_node, duration, browser_type=node_browser_type,
                             browser_version=node_browser_version)
        try:
            artefacts_client.upload_test_details(test_data.to_json())
        except Exception as e:
            test_context.logger.error(e)

        # upload log
        log = Log(session_id, test_context.log_text)
        try:
            artefacts_client.upload_log(log.to_json())
        except Exception as e:
            test_context.logger.error(e)

        # output report URL
        test_report = artefacts_client.get_test_report_uri(session_id)
        session_report = artefacts_client.get_test_run_report_uri(test_session_guid)
        test_context.logger.info(
            "This test report: <a href=\"{}\" target=\"_blank\">{}</a>".format(test_report, REPORT_LINK_SG_TEST))
        test_context.logger.info(
            "This test session: <a href=\"{}\" target=\"_blank\">{}</a>".format(session_report, REPORT_LINK_SG_SESSION))