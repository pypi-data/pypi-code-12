#!/usr/bin/env python
"""This file contains utility classes related to maintenance used by GRR."""



import getpass
import hashlib
import os
import StringIO
import time
import zipfile


import logging

from grr.lib import access_control
from grr.lib import aff4
from grr.lib import build
from grr.lib import config_lib
from grr.lib import rdfvalue
from grr.lib import utils
from grr.lib.aff4_objects import collects
from grr.lib.builders import signing
from grr.lib.rdfvalues import client as rdf_client
from grr.lib.rdfvalues import crypto as rdf_crypto


DIGEST_ALGORITHM = hashlib.sha256  # pylint: disable=invalid-name
DIGEST_ALGORITHM_STR = "sha256"

SUPPORTED_PLATFORMS = ["windows", "linux", "darwin"]
SUPPORTED_ARCHITECTURES = ["i386", "amd64"]


def UploadSignedConfigBlob(content, aff4_path, client_context=None,
                           limit=None, token=None):
  """Upload a signed blob into the datastore.

  Args:
    content: File content to upload.
    aff4_path: aff4 path to upload to.
    client_context: The configuration contexts to use.
    limit: The maximum size of the chunk to use.
    token: A security token.

  Raises:
    IOError: On failure to write.
  """
  if limit is None:
    limit = config_lib.CONFIG["Datastore.maximum_blob_size"]

  # Get the values of these parameters which apply to the client running on the
  # target platform.
  if client_context is None:
    # Default to the windows client.
    client_context = ["Platform:Windows", "Client Context"]

  config_lib.CONFIG.Validate(
      parameters="PrivateKeys.executable_signing_private_key")

  sig_key = config_lib.CONFIG.Get("PrivateKeys.executable_signing_private_key",
                                  context=client_context)

  ver_key = config_lib.CONFIG.Get("Client.executable_signing_public_key",
                                  context=client_context)

  urn = collects.GRRSignedBlob.NewFromContent(
      content, aff4_path, chunk_size=limit, token=token,
      private_key=sig_key, public_key=ver_key)

  logging.info("Uploaded to %s", urn)


def UploadSignedDriverBlob(content, aff4_path=None, client_context=None,
                           install_request=None, token=None):
  """Upload a signed blob into the datastore.

  Args:
    content: Content of the driver file to upload.

    aff4_path: aff4 path to upload to. If not specified, we use the config to
      figure out where it goes.

    client_context: The configuration contexts to use.

    install_request: A DriverInstallRequest rdfvalue describing the installation
      parameters for this driver. If None these are read from the config.

    token: A security token.

  Returns:
    String containing path the file was written to.

  Raises:
    IOError: On failure to write.
  """
  sig_key = config_lib.CONFIG.Get("PrivateKeys.driver_signing_private_key",
                                  context=client_context)

  ver_key = config_lib.CONFIG.Get("Client.driver_signing_public_key",
                                  context=client_context)

  if aff4_path is None:
    aff4_paths = config_lib.CONFIG.Get("MemoryDriver.aff4_paths",
                                       context=client_context)
    if not aff4_paths:
      raise IOError("Could not determine driver location.")
    if len(aff4_paths) > 1:
      logging.info("Possible driver locations: %s", aff4_paths)
      raise IOError("Ambiguous driver location, please specify.")
    aff4_path = aff4_paths[0]

  blob_rdf = rdf_crypto.SignedBlob()
  blob_rdf.Sign(content, sig_key, ver_key, prompt=True)

  with aff4.FACTORY.Create(
      aff4_path, "GRRMemoryDriver", mode="w", token=token) as fd:
    fd.Add(blob_rdf)

    if install_request is None:
      # Create install_request from the configuration.
      install_request = rdf_client.DriverInstallTemplate(
          device_path=config_lib.CONFIG.Get(
              "MemoryDriver.device_path", context=client_context),
          driver_display_name=config_lib.CONFIG.Get(
              "MemoryDriver.driver_display_name", context=client_context),
          driver_name=config_lib.CONFIG.Get(
              "MemoryDriver.driver_service_name", context=client_context))

    fd.Set(fd.Schema.INSTALLATION(install_request))

  logging.info("Uploaded to %s", fd.urn)

  return fd.urn


def GetConfigBinaryPathType(aff4_path):
  """Take an aff4_path and return type or None.

  Args:
    aff4_path: An RDFURN containing the path to the binary.

  Returns:
    None if the path is not supported for binary upload, otherwise a type.
  """
  if not aff4_path.Path().startswith("/config"):
    return
  components = aff4_path.RelativeName("aff4:/config").split("/")
  if components[0] == "drivers" and components[1] in SUPPORTED_PLATFORMS:
    return "GRRMemoryDriver"
  elif components[0] == "executables" and components[1] in SUPPORTED_PLATFORMS:
    return "GRRSignedBlob"
  elif components[0] == "python_hacks":
    return "GRRSignedBlob"
  else:
    return


def CreateBinaryConfigPaths(token=None):
  """Create the paths required for binary configs."""
  required_urns = set()

  try:
    # We weren't already initialized, create all directories we will need.
    for platform in SUPPORTED_PLATFORMS:
      for arch in SUPPORTED_ARCHITECTURES:
        client_context = ["Platform:%s" % platform.title(),
                          "Arch:%s" % arch]

        aff4_paths = config_lib.CONFIG.Get("MemoryDriver.aff4_paths",
                                           context=client_context)
        for aff4_path in aff4_paths:
          required_urns.add(rdfvalue.RDFURN(aff4_path).Dirname())

      required_urns.add("aff4:/config/executables/%s/agentupdates" % platform)
      required_urns.add("aff4:/config/executables/%s/installers" % platform)

    existing_urns = [x["urn"] for x in aff4.FACTORY.Stat(list(required_urns),
                                                         token=token)]

    missing_urns = required_urns - set(existing_urns)

    # One by one is not optimal but we have to do it only once per urn.
    for urn in missing_urns:
      aff4.FACTORY.Create(urn, "AFF4Volume", token=token).Flush()

  except access_control.UnauthorizedAccess:
    logging.info("User is not admin, cannot check configuration tree.")
    return


def _RepackBinary(context, builder_cls):
  # Check for the presence of the template.
  template_path = config_lib.CONFIG.Get("ClientBuilder.template_path",
                                        context=context)

  if os.path.exists(template_path):
    builder_obj = builder_cls(context=context)
    try:
      return builder_obj.MakeDeployableBinary(template_path)
    except Exception as e:  # pylint: disable=broad-except
      print "Repacking template %s failed: %s" % (template_path, e)
  else:
    print "Template %s missing - will not repack." % template_path


def RepackAllBinaries(upload=False, debug_build=False, token=None):
  """Repack binaries based on the configuration.

  NOTE: The configuration file specifies the location of the binaries
  templates. These usually depend on the client version which is also specified
  in the configuration file. This simple function simply runs through all the
  supported architectures looking for available templates for the configured
  client version, architecture and operating system.

  We do not repack all the binaries that are found in the template directories,
  only the ones that are valid for the current configuration. It is not an error
  to have a template missing, we simply ignore it and move on.

  Args:
    upload: If specified we also upload the repacked binary into the datastore.
    debug_build: Repack as a debug build.
    token: Token to use when uploading

  Returns:
    A list of output installers generated.
  """
  built = []

  base_context = ["ClientBuilder Context"]
  if debug_build:
    base_context += ["DebugClientBuild Context"]

  clients_to_repack = [
      (["Target:Windows", "Platform:Windows", "Arch:amd64"],
       build.WindowsClientDeployer),
      (["Target:Windows", "Platform:Windows", "Arch:i386"],
       build.WindowsClientDeployer),
      (["Target:Linux", "Platform:Linux", "Arch:amd64"],
       build.LinuxClientDeployer),
      (["Target:Linux", "Platform:Linux", "Arch:i386"],
       build.LinuxClientDeployer),
      (["Target:Linux", "Target:LinuxRpm", "Platform:Linux", "Arch:amd64"],
       build.CentosClientDeployer),
      (["Target:Linux", "Target:LinuxRpm", "Platform:Linux", "Arch:i386"],
       build.CentosClientDeployer),
      (["Target:Darwin", "Platform:Darwin", "Arch:amd64"],
       build.DarwinClientDeployer)]

  msg = "Will repack the following clients "
  if debug_build:
    msg += "(debug build)"
  print msg + ":"
  print

  for context, deployer in clients_to_repack:
    context = base_context + context

    template_path = config_lib.CONFIG.Get("ClientBuilder.template_path",
                                          context=context)
    output_path = config_lib.CONFIG.Get("ClientBuilder.output_path",
                                        context=context)
    readable = (os.path.isfile(template_path) and
                os.access(template_path, os.R_OK))

    if not readable:
      readable_str = " (NOT READABLE)"
    else:
      readable_str = ""
    print "Repacking : " + template_path + readable_str
    print "To :        " + output_path
    print

  for context, deployer in clients_to_repack:
    context = base_context + context
    template_path = config_lib.CONFIG.Get("ClientBuilder.template_path",
                                          context=context)
    output_path = _RepackBinary(context, deployer)
    if output_path:
      print "%s repacked ok." % template_path
      built.append(output_path)
      if upload:
        dest = config_lib.CONFIG.Get("Executables.installer",
                                     context=context)
        UploadSignedConfigBlob(open(output_path).read(100 * 1024 * 1024),
                               dest, client_context=context, token=token)
    else:
      print "Failed to repack %s." % template_path

  return built


def _SignWindowsComponent(component, output_filename):
  print "Enter passphrase for code signing cert:"
  passwd = getpass.getpass()
  cert = config_lib.CONFIG.Get("ClientBuilder.windows_signing_cert")
  key = config_lib.CONFIG.Get("ClientBuilder.windows_signing_key")
  app_name = config_lib.CONFIG.Get(
      "ClientBuilder.windows_signing_application_name")

  signer = signing.WindowsCodeSigner(cert, key, passwd, app_name)
  with utils.TempDirectory() as temp_dir:
    zip_file = zipfile.ZipFile(StringIO.StringIO(component.raw_data))
    zip_file.extractall(temp_dir)

    new_data = StringIO.StringIO()
    new_zipfile = zipfile.ZipFile(new_data, mode="w",
                                  compression=zipfile.ZIP_DEFLATED)

    for root, _, files in os.walk(temp_dir):
      for basename in files:
        basename = basename.lstrip("\\/")
        filename = os.path.join(root, basename)

        # The relative filename to the root of the zip file.
        relative_filename = filename[len(temp_dir):].lstrip("/")

        extension = os.path.splitext(filename)[1].lower()
        if extension in [".sys", ".exe", ".dll", ".pyd"]:
          out_filename = filename + ".signed"
          signer.SignFile(filename, out_filename=out_filename)
          new_zipfile.write(out_filename, arcname=relative_filename)
        else:
          new_zipfile.write(filename, arcname=relative_filename)

    # Flush the Zip file.
    new_zipfile.close()
    component.raw_data = new_data.getvalue()

    with open(output_filename, "wb") as out_fd:
      out_fd.write(component.SerializeToString())


def SignComponentContent(component_filename, output_filename):
  """Some OSs require the contents of a component to be signed as well.

  Specifically this action unzips the component and authenticode signs all
  binaries. The component is then repacked.

  Args:
    component_filename: The filename of the component.
    output_filename: We write the new signed component here.

  Raises:
    RuntimeError: If called for any other OS than windows.
  """
  component = rdf_client.ClientComponent(open(component_filename).read())
  print "Opened component %s." % component.summary.name

  if component.build_system.system == "Windows":
    _SignWindowsComponent(component, output_filename)
    return

  raise RuntimeError("Component signing is not implemented for OS %s." %
                     component.build_system.system)


def SignComponent(component_filename, overwrite=False, token=None):
  """Sign and upload the component to the data store."""

  print "Signing and uploading component %s" % component_filename
  component = rdf_client.ClientComponent(open(component_filename).read())
  print "Opened component %s." % component.summary.name

  client_context = ["Platform:%s" % component.build_system.system.title(),
                    "Arch:%s" % component.build_system.arch]

  sig_key = config_lib.CONFIG.Get(
      "PrivateKeys.executable_signing_private_key",
      context=client_context)

  ver_key = config_lib.CONFIG.Get("Client.executable_signing_public_key",
                                  context=client_context)

  # For each platform specific component, we have a component summary object
  # which contains high level information in common to all components of this
  # specific version.
  component_urn = config_lib.CONFIG.Get(
      "Config.aff4_root").Add("components").Add(
          "%s_%s" % (component.summary.name, component.summary.version))

  component_fd = aff4.FACTORY.Create(component_urn, "ComponentObject",
                                     mode="rw", token=token)

  component_summary = component_fd.Get(component_fd.Schema.COMPONENT)
  if overwrite or component_summary is None:
    print "Storing component summary at %s" % component_urn

    component_summary = component.summary
    component_summary.seed = "%x%x" % (time.time(), utils.PRNG.GetULong())
    component_summary.url = (
        config_lib.CONFIG.Get(
            "Client.component_url_stem",
            context=client_context) + component_summary.seed)

    component_fd.Set(component_fd.Schema.COMPONENT, component_summary)
    component_fd.Close()

  else:
    print "Using seed from stored component summary at %s" % component_urn
    component.summary.url = component_summary.url
    component.summary.seed = component_summary.seed

  # Sign the component, encrypt it and store it at the static aff4 location.
  signed_component = rdf_crypto.SignedBlob()
  signed_component.Sign(component.SerializeToString(), sig_key, ver_key,
                        prompt=True)

  aff4_urn = config_lib.CONFIG.Get(
      "Client.component_aff4_stem", context=client_context).Add(
          component.summary.seed).Add(component.build_system.signature())

  print "Storing signed component at %s" % aff4_urn
  with aff4.FACTORY.Create(aff4_urn, "AFF4MemoryStream", token=token) as fd:
    fd.Write(component_summary.cipher.Encrypt(
        signed_component.SerializeToString()))

  return component


def SignAllComponents(overwrite=False, token=None):

  components_dir = config_lib.CONFIG["ClientBuilder.components_dir"]
  for root, _, files in os.walk(components_dir):
    for f in files:
      if os.path.splitext(f)[1] != ".bin":
        continue

      component_filename = os.path.join(root, f)
      try:
        SignComponent(component_filename, overwrite=overwrite, token=token)
      except Exception as e:  # pylint: disable=broad-except
        print "Could not sign component %s: %s" % (component_filename, e)
