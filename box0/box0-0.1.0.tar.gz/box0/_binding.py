#
# This file is part of pyBox0.
# Copyright (C) 2014, 2015 Kuldeep Singh Dhaka <kuldeepdhaka9@gmail.com>
#
# pyBox0 is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pyBox0 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pyBox0.  If not, see <http://www.gnu.org/licenses/>.
#

import cffi
import codecs

ffi = cffi.FFI()

ffi.cdef("""
	/* libusb structs
	 * Note: not a part of libbox0 api */
	typedef struct libusb_device libusb_device;
	typedef struct libusb_device_handle libusb_device_handle;

	/* we are less intrested in inside content */
	typedef struct b0_device b0_device;
	typedef struct b0_ain b0_ain;
	typedef struct b0_aout b0_aout;
	typedef struct b0_spi b0_spi;
	typedef struct b0_i2c b0_i2c;
	typedef struct b0_pwm b0_pwm;
	typedef struct b0_dio b0_dio;
	typedef struct b0_stream_value b0_stream_value;
	typedef struct b0_stream b0_stream;
	typedef struct b0_ref b0_ref;
	typedef struct b0_bitsize b0_bitsize;
	typedef struct b0_speed b0_speed;
	typedef struct b0_chan_config b0_chan_config;
	typedef struct b0_chan_seq b0_chan_seq;
	typedef struct b0_count b0_count;
	typedef struct b0_capab b0_capab;
	typedef struct b0_buffer b0_buffer;
	typedef struct b0_i2c_version b0_i2c_version;
	typedef struct b0_label_value b0_label_value;
	typedef struct b0_label b0_label;
	typedef struct b0_repeat b0_repeat;
	typedef struct b0_module b0_module;
	typedef struct b0_dio b0_dio;
	typedef struct b0_i2c b0_i2c;
	typedef struct b0_spi b0_spi;
	typedef struct b0_unio b0_unio;
	typedef struct b0_version b0_version;
	typedef struct b0_property b0_property;

	typedef struct b0_hbridge b0_hbridge;
	typedef struct b0_adxl345 b0_adxl345;
	typedef struct b0_mcp342x b0_mcp342x;
	typedef struct b0_ads1220 b0_ads1220;

	/* this should have been "typedef enum b0_result_code b0_result_code;"
	  but the value is interpretted as unsigned (instead of int)
	  see: https://bitbucket.org/cffi/cffi/issues/230 */
	typedef int b0_result_code;

	#define B0_OK 0
	#define B0_ERR_UNAVAIL -16
	#define B0_ERR_SEARCH -20

	enum b0_module_type {
		B0_DIO = 1,
		B0_AOUT = 2,
		B0_AIN = 3,
		B0_SPI = 4,
		B0_I2C = 5,
		B0_PWM = 6,
		B0_UNIO = 7
	};

	typedef enum b0_module_type b0_module_type;

	enum b0_property_type {
		B0_STREAM = -2,
		B0_CHAN_SEQ = -1,
		B0_REF = 1,
		B0_SPEED = 2,
		B0_BITSIZE = 3,
		B0_CAPAB = 4,
		B0_COUNT = 5,
		B0_LABEL = 6,
		B0_BUFFER = 7,
		B0_REPEAT = 8,
		B0_CHAN_CONFIG = 9,

		B0_I2C_VERSION = 101,

		B0_PWM_INITAL = 101,
		B0_PWM_SYMMERTRIC = 102,
	};

	typedef enum b0_property_type b0_property_type;

	struct b0_device {
		size_t modules_len;
		b0_module **modules;
		uint8_t *name;
		uint8_t *manuf;
		uint8_t *serial;
	};

	struct b0_module {
		b0_module_type type;
		int index;
		uint8_t *name;
		b0_device *device;
		void *backend_data;
		void *frontend_data;
	};

	/* modules */
	struct b0_ain {
		b0_module header;
		b0_bitsize *bitsize;
		b0_buffer *buffer;
		b0_capab *capab;
		b0_count *count;
		b0_chan_config *chan_config;
		b0_chan_seq *chan_seq;
		b0_label *label;
		b0_ref *ref;
		b0_speed *speed;
		b0_stream *stream;
	};

	struct b0_aout {
		b0_module header;
		b0_bitsize *bitsize;
		b0_buffer *buffer;
		b0_capab *capab;
		b0_count *count;
		b0_chan_config *chan_config;
		b0_chan_seq *chan_seq;
		b0_label *label;
		b0_ref *ref;
		b0_repeat *repeat;
		b0_speed *speed;
		b0_stream *stream;
	};

	/* properties */
	struct b0_property {
		b0_property_type type;
		b0_module *module;
		void *backend_data;
		void *frontend_data;
	};

	struct b0_stream_value {
		uint32_t speed;
		uint8_t bitsize;
		void *backend_data;
		void *frontend_data;
	};

	struct b0_stream {
		b0_property header;
		size_t values_len;
		b0_stream_value *values;
	};

	struct b0_buffer {
		b0_property header;
		uint32_t value;
	};

	struct b0_count {
		b0_property header;
		uint32_t value;
	};

	enum b0_ref_type {
		B0_REF_VOLTAGE = 0,
		B0_REF_CURRENT = 1
	};

	typedef enum b0_ref_type b0_ref_type;

	struct b0_ref {
		b0_property header;
		b0_ref_type type;
		double low, high;
	};

	enum b0_i2c_version_value {
		B0_I2C_VERSION_SM = 0,
		B0_I2C_VERSION_FM = 1,
		B0_I2C_VERSION_HS = 2,
		B0_I2C_VERSION_HS_CLEANUP1 = 3,
		B0_I2C_VERSION_FMPLUS = 4,
		B0_I2C_VERSION_UFM = 5,
		B0_I2C_VERSION_VER5 = 6,
		B0_I2C_VERSION_VER6 = 7
	};

	typedef enum b0_i2c_version_value b0_i2c_version_value;

	struct b0_i2c_version {
		b0_property header;
		size_t values_len;
		b0_i2c_version_value *values;
	};

	struct b0_label {
		b0_property header;
		size_t values_len;
		uint8_t **values;
	};

	struct b0_repeat {
		b0_property header;
		size_t values_len;
		uint8_t *values;
	};

	struct b0_bitsize {
		b0_property header;
		size_t values_len;
		uint8_t *values;
	};

	struct b0_speed {
		b0_property header;
		size_t values_len;
		uint32_t *values;
	};

	struct b0_pwm {
		b0_module header;
		b0_bitsize *bitsize;
		b0_capab *capab;
		b0_count *count;
		b0_label *label;
		b0_ref *ref;
		b0_speed *speed;
	};

	typedef uintmax_t b0_pwm_reg;

	struct b0_dio {
		b0_module header;
		b0_capab *capab;
		b0_count *count;
		b0_label *label;
		b0_ref *ref;
	};

	struct b0_i2c {
		b0_module header;
		b0_buffer *buffer;
		b0_label *label;
		b0_ref *ref;
		b0_i2c_version *version;
	};

	struct b0_spi {
		b0_module header;
		b0_bitsize *bitsize;
		b0_buffer *buffer;
		b0_capab *capab;
		b0_count *count;
		b0_label *label;
		b0_ref *ref;
		b0_speed *speed;
	};

	struct b0_unio {
		b0_module header;
		b0_buffer *buffer;
		b0_capab *capab;
		b0_label *label;
		b0_ref *ref;
		b0_speed *speed;
	};

	/* constants that need to be accessed [used for b0_device_log()] */
	enum b0_log_level {
		B0_LOG_NONE = 0,
		B0_LOG_ERROR = 1,
		B0_LOG_WARN = 2,
		B0_LOG_INFO = 3,
		B0_LOG_DEBUG = 4
	};

	typedef enum b0_log_level b0_log_level;

	#define B0_DIO_HIGH 1
	#define B0_DIO_LOW 0

	#define B0_DIO_OUTPUT 1
	#define B0_DIO_INPUT 0

	#define B0_DIO_ENABLE 1
	#define B0_DIO_DISABLE 0

	/* H-Bridge values */
	enum {
		/* primitve values */
		B0_HBRIDGE_EN = 0x01,
		B0_HBRIDGE_A1 = 0x02,
		B0_HBRIDGE_A2 = 0x04,

		/* Higher level functions */
		B0_HBRIDGE_DISABLE = 0x00,
		B0_HBRIDGE_FORWARD = 0x03 /* B0_HBRIDGE_EN | B0_HBRIDGE_A1 */,
		B0_HBRIDGE_BACKWARD = 0x05 /* B0_HBRIDGE_EN | B0_HBRIDGE_A2 */,
	};

	/* MCP342x */
	enum b0_mcp342x_adr {
		B0_MCP342X_LOW = 0,
		B0_MCP342X_FLOAT = 1,
		B0_MCP342X_HIGH = 2
	};

	enum b0_mcp342x_chan {
		B0_MCP342X_CH1 = 0,
		B0_MCP342X_CH2 = 1,
		B0_MCP342X_CH3 = 2,
		B0_MCP342X_CH4 = 3
	};

	enum b0_mcp342x_gain {
		B0_MCP342X_GAIN1 = 0,
		B0_MCP342X_GAIN2 = 1,
		B0_MCP342X_GAIN4 = 2,
		B0_MCP342X_GAIN8 = 3
	};

	enum b0_mcp342x_samp_rate {
		B0_MCP342X_SAMP_RATE_240 = 0,
		B0_MCP342X_SAMP_RATE_60 = 1,
		B0_MCP342X_SAMP_RATE_15 = 2
	};

	typedef enum b0_mcp342x_adr b0_mcp342x_adr;
	typedef enum b0_mcp342x_chan b0_mcp342x_chan;
	typedef enum b0_mcp342x_gain b0_mcp342x_gain;
	typedef enum b0_mcp342x_samp_rate b0_mcp342x_samp_rate;

	/* ADS1220 */
	enum b0_ads1220_filter {
		B0_ADS1220_FILTER_NONE = 0,
		B0_ADS1220_FILTER_50HZ = 1,
		B0_ADS1220_FILTER_60HZ = 2,
		B0_ADS1220_FILTER_50HZ_60HZ = 3
	};

	enum b0_ads1220_vref_source {
		B0_ADS1220_VREF_INTERNAL = 0,
		B0_ADS1220_VREF_REFP0_REFN0 = 1,
		B0_ADS1220_VREF_REFP1_REFN1 = 2,
		B0_ADS1220_VREF_AVDD_AVSS = 3
	};

	enum b0_ads1220_gain {
		B0_ADS1220_GAIN_1 = 0,
		B0_ADS1220_GAIN_2 = 1,
		B0_ADS1220_GAIN_4 = 2,
		B0_ADS1220_GAIN_8 = 3,
		B0_ADS1220_GAIN_16 = 4,
		B0_ADS1220_GAIN_32 = 5,
		B0_ADS1220_GAIN_64 = 6,
		B0_ADS1220_GAIN_128 = 7
	};

	typedef enum b0_ads1220_filter b0_ads1220_filter;
	typedef enum b0_ads1220_gain b0_ads1220_gain;
	typedef enum b0_ads1220_vref_source b0_ads1220_vref_source;

	struct b0_version {
		uint8_t major;
		uint8_t minor;
		uint8_t patch;
	};

	#define B0_BOX0V5_PS_PM5 0x01 /* ±5 power supply */
	#define B0_BOX0V5_PS_P3  0x02 /* +3 power supply */

	/* module */
	b0_result_code b0_module_info(b0_module *mod);
	b0_result_code b0_module_openable(b0_module *mod);

	/* user accessible method for device */
	b0_result_code b0_device_info(b0_device *dev);
	b0_result_code b0_device_close(b0_device *dev);
	b0_result_code b0_device_log(b0_device *dev, b0_log_level level);

	b0_result_code b0_device_ping(b0_device *dev);

	/* function for result codes */
	const uint8_t* b0_result_name(b0_result_code r);
	const uint8_t* b0_result_explain(b0_result_code r);

	/* AIN related */
	b0_result_code b0_ain_info(b0_ain *mod);
	b0_result_code b0_ain_close(b0_ain *mod);
	b0_result_code b0_ain_open(b0_device *dev, b0_ain **mod, int index);
	b0_result_code b0_ain_cache_flush(b0_ain *mod);

	/* AIN stream API */
	b0_result_code b0_ain_stream_prepare(b0_ain *mod, b0_stream_value *stream);
	b0_result_code b0_ain_stream_start(b0_ain *mod);
	b0_result_code b0_ain_stream_read(b0_ain *mod, void *samples, size_t count, size_t *actual_len);
	b0_result_code b0_ain_stream_read_float(b0_ain *mod, float *samples, size_t count, size_t *actual_len);
	b0_result_code b0_ain_stream_read_double(b0_ain *mod, double *samples, size_t count, size_t *actual_len);
	b0_result_code b0_ain_stream_stop(b0_ain *mod);

	/* AIN static API */
	b0_result_code b0_ain_static_prepare(b0_ain *mod);
	b0_result_code b0_ain_static_start(b0_ain *mod, void *buffer, size_t buffer_data);
	b0_result_code b0_ain_static_start_double(b0_ain *mod, double *buffer, size_t buffer_data);
	b0_result_code b0_ain_static_start_float(b0_ain *mod, float *buffer, size_t buffer_data);
	b0_result_code b0_ain_static_stop(b0_ain *mod);

	/* property: stream speed API */
	b0_result_code b0_stream_search(b0_stream *prop, b0_stream_value **value, uint32_t speed, uint8_t bitsize);

	/* AOUT API */
	b0_result_code b0_aout_cache_flush(b0_aout *mod);
	b0_result_code b0_aout_info(b0_aout *mod);
	b0_result_code b0_aout_close(b0_aout *mod);
	b0_result_code b0_aout_open(b0_device *dev, b0_aout **mod, int index);

	/* AOUT: stream API */
	b0_result_code b0_aout_stream_prepare(b0_aout *mod, b0_stream_value *stream_value);
	b0_result_code b0_aout_stream_write(b0_aout *mod, void *data, size_t len);
	b0_result_code b0_aout_stream_write_double(b0_aout *mod, double *data, size_t len);
	b0_result_code b0_aout_stream_write_float(b0_aout *mod, float *data, size_t len);
	b0_result_code b0_aout_stream_start(b0_aout *mod);
	b0_result_code b0_aout_stream_stop(b0_aout *mod);

	/* AOUT: static API */
	b0_result_code b0_aout_static_prepare(b0_aout *mod);
	b0_result_code b0_aout_static_start(b0_aout *mod, void *data, size_t len);
	b0_result_code b0_aout_static_start_double(b0_aout *mod, double *data, size_t len);
	b0_result_code b0_aout_static_start_float(b0_aout *mod, float *data, size_t len);
	b0_result_code b0_aout_static_stop(b0_aout *mod);
	b0_result_code b0_aout_static_calc(b0_aout *mod, double freq,
			uint8_t bitsize, size_t *count, uint32_t *speed);

	/* Property: buffer */
	b0_result_code b0_buffer_cache_flush(b0_buffer *prop);
	b0_result_code b0_buffer_info(b0_buffer *prop);

	/* property: channel sequence */
	b0_result_code b0_chan_seq_info(b0_chan_seq *prop);
	b0_result_code b0_chan_seq_cache_flush(b0_chan_seq *prop);
	b0_result_code b0_chan_seq_get(b0_chan_seq *prop, uint8_t *list, size_t *list_len);
	b0_result_code b0_chan_seq_set(b0_chan_seq *prop, uint8_t *list, size_t list_len);

	/* property: count */
	b0_result_code b0_count_info(b0_count *prop);
	b0_result_code b0_count_cache_flush(b0_count *prop);

	/* property: ref */
	b0_result_code b0_ref_info(b0_ref *prop);
	b0_result_code b0_ref_cache_flush(b0_ref *prop);

	/* property: i2c version */
	b0_result_code b0_i2c_version_set(b0_i2c_version *prop, uint8_t version);
	b0_result_code b0_i2c_version_get(b0_i2c_version *prop, uint8_t *version);
	b0_result_code b0_i2c_version_cache_flush(b0_i2c_version *prop);
	b0_result_code b0_i2c_version_info(b0_i2c_version *prop);

	/* Property: label */
	b0_result_code b0_label_info(b0_label *prop);
	b0_result_code b0_label_cache_flush(b0_label *prop);

	/* Property: stream speed */
	b0_result_code b0_stream_info(b0_stream *prop);
	b0_result_code b0_stream_cache_flush(b0_stream *prop);

	/* Property: repeat */
	b0_result_code b0_repeat_set(b0_repeat *prop, uint32_t output);
	b0_result_code b0_repeat_get(b0_repeat *prop, uint32_t *output);
	b0_result_code b0_repeat_cache_flush(b0_repeat *prop);
	b0_result_code b0_repeat_info(b0_repeat *prop);

	/* Property: Bitsize */
	b0_result_code b0_bitsize_set(b0_bitsize *prop, uint8_t value);
	b0_result_code b0_bitsize_get(b0_bitsize *prop, uint8_t *value);
	b0_result_code b0_bitsize_cache_flush(b0_bitsize *prop);
	b0_result_code b0_bitsize_info(b0_bitsize *prop);

	/* Property: Speed */
	b0_result_code b0_speed_info(b0_speed *prop);
	b0_result_code b0_speed_cache_flush(b0_speed *prop);
	b0_result_code b0_speed_set(b0_speed *property, uint32_t speed);
	b0_result_code b0_speed_get(b0_speed *property, uint32_t *speed);

	/* Module: PWM */
	b0_result_code b0_pwm_cache_flush(b0_pwm *mod);
	b0_result_code b0_pwm_info(b0_pwm *mod);
	b0_result_code b0_pwm_close(b0_pwm *mod);
	b0_result_code b0_pwm_open(b0_device *dev, b0_pwm **mod, int index);
	b0_result_code b0_pwm_width_set(b0_pwm *mod, uint8_t width_index, b0_pwm_reg width);
	b0_result_code b0_pwm_width_get(b0_pwm *mod, uint8_t width_index, b0_pwm_reg *width);
	b0_result_code b0_pwm_period_set(b0_pwm *mod, b0_pwm_reg period);
	b0_result_code b0_pwm_period_get(b0_pwm *mod, b0_pwm_reg *period);
	b0_result_code b0_pwm_set(b0_pwm *mod, uint8_t ch, double *freq_user,
						double *duty_cycle, double *error_user);
	b0_result_code b0_pwm_calc(b0_pwm *mod, double freq_user,
						double error, uint32_t *speed, b0_pwm_reg *period);
	b0_result_code b0_pwm_start(b0_pwm *mod);
	b0_result_code b0_pwm_stop(b0_pwm *mod);

	/* Module : DIO */
	b0_result_code b0_dio_info(b0_dio *mod);
	b0_result_code b0_dio_cache_flush(b0_dio *mod);
	b0_result_code b0_dio_close(b0_dio *mod);
	b0_result_code b0_dio_open(b0_device *dev, b0_dio **mod, int index);
	b0_result_code b0_dio_static_prepare(b0_dio *mod);
	b0_result_code b0_dio_value_get(b0_dio *mod, uint8_t pin, bool *value);
	b0_result_code b0_dio_value_set(b0_dio *mod, uint8_t pin, bool value);
	b0_result_code b0_dio_value_toggle(b0_dio *mod, uint8_t pin);
	b0_result_code b0_dio_dir_get(b0_dio *mod, uint8_t pin, bool *value);
	b0_result_code b0_dio_dir_set(b0_dio *mod, uint8_t pin, bool value);
	b0_result_code b0_dio_hiz_get(b0_dio *mod, uint8_t pin, bool *value);
	b0_result_code b0_dio_hiz_set(b0_dio *mod, uint8_t pin, bool value);

	b0_result_code b0_dio_multiple_value_set(b0_dio *mod,
				uint8_t *pins, size_t size, bool value);
	b0_result_code b0_dio_multiple_value_get(b0_dio *mod,
				uint8_t *pins, bool *values, size_t size);
	b0_result_code b0_dio_multiple_value_toggle(b0_dio *mod,
				uint8_t *pins, size_t size);
	b0_result_code b0_dio_multiple_dir_set(b0_dio *mod,
				uint8_t *pins, size_t size, bool value);
	b0_result_code b0_dio_multiple_dir_get(b0_dio *mod,
				uint8_t *pins, bool *values, size_t size);
	b0_result_code b0_dio_multiple_hiz_get(b0_dio *mod,
				uint8_t *pins, bool *values, size_t size);
	b0_result_code b0_dio_multiple_hiz_set(b0_dio *mod,
				uint8_t *pins, size_t size, bool value);

	b0_result_code b0_dio_all_value_set(b0_dio *mod, bool value);
	b0_result_code b0_dio_all_value_get(b0_dio *mod, bool *values);
	b0_result_code b0_dio_all_value_toggle(b0_dio *mod);
	b0_result_code b0_dio_all_dir_set(b0_dio *mod, bool value);
	b0_result_code b0_dio_all_dir_get(b0_dio *mod, bool *values);
	b0_result_code b0_dio_all_hiz_get(b0_dio *mod, bool *values);
	b0_result_code b0_dio_all_hiz_set(b0_dio *mod, bool value);

	/* Module: I2C */
	b0_result_code b0_i2c_info(b0_i2c *mod);
	b0_result_code b0_i2c_cache_flush(b0_i2c *mod);
	b0_result_code b0_i2c_close(b0_i2c *mod);
	b0_result_code b0_i2c_open(b0_device *dev, b0_i2c **mod, int index);
	b0_result_code b0_i2c_start(b0_i2c *mod, void * send, size_t send_len,
		void *recv, size_t recv_len, size_t *user_actual_len);
	b0_result_code b0_i2c_start_out(b0_i2c *mod, void * send, size_t send_len);
	b0_result_code b0_i2c_stop(b0_i2c *mod);
	b0_result_code b0_i2c_read(b0_i2c *mod, uint8_t bSlaveAddress,
						uint8_t *bData, uint8_t bRead);
	b0_result_code b0_i2c_write(b0_i2c *mod, uint8_t bSlaveAddress,
						uint8_t *bData, uint8_t bWrite);
	b0_result_code b0_i2c_write8_read(b0_i2c *mod, uint8_t bSlaveAddress,
		uint8_t bData_write, uint8_t *bData_read, uint8_t bWrite);
	b0_result_code b0_i2c_slave_id(b0_i2c *mod, uint8_t bSlaveAddress,
		uint16_t *manuf, uint16_t *part, uint8_t *rev);
	b0_result_code b0_i2c_slave_detect(b0_i2c *mod, uint8_t bSlaveAddress, bool *detected);

	/* Module: SPI */
	b0_result_code b0_spi_info(b0_spi *mod);
	b0_result_code b0_spi_cache_flush(b0_spi *mod);
	b0_result_code b0_spi_close(b0_spi *mod);
	b0_result_code b0_spi_open(b0_device *dev, b0_spi **mod, int index);
	b0_result_code b0_spi_start(b0_spi *mod, void *send, size_t send_len,
			void *recv, size_t recv_len, size_t *actual_recv_len);
	b0_result_code b0_spi_start_out(b0_spi *mod, void *send, size_t send_len);
	b0_result_code b0_spi_stop(b0_spi *mod);
	b0_result_code b0_spi_active_state_set(b0_spi *mod, uint8_t ss, bool value);
	b0_result_code b0_spi_active_state_get(b0_spi *mod, uint8_t ss, bool *value);

	/* Module: UNIO */
	b0_result_code b0_unio_info(b0_unio *mod);
	b0_result_code b0_unio_cache_flush(b0_unio *mod);
	b0_result_code b0_unio_open(b0_device *dev, b0_unio **mod, int index);
	b0_result_code b0_unio_close(b0_unio *mod);
	b0_result_code b0_unio_start(b0_unio *mod, void *send, size_t send_len,
			void *recv, size_t recv_len, size_t *actual_recv_len);
	b0_result_code b0_unio_start_out(b0_unio *mod, void *send, size_t send_len);
	b0_result_code b0_unio_stop(b0_unio *mod);
	b0_result_code b0_unio_slave_detect(b0_unio *mod, uint8_t bSlaveAddress, bool *available);

	b0_result_code b0_unio_read(b0_unio *mod, uint8_t bSlaveAddress,
		uint8_t *bData, uint8_t bRead);
	b0_result_code b0_unio_write(b0_unio *mod, uint8_t bSlaveAddress,
		uint8_t *bData, uint8_t bWrite);
	b0_result_code b0_unio_write8_read(b0_unio *mod,
		uint8_t bSlaveAddress, uint8_t bData_write,
		uint8_t *bData_read, uint8_t bWrite);

	uint32_t b0_version_extract(b0_version *ver);

	/* libusb */
	typedef struct libusb_device_handle libusb_device_handle;
	typedef struct libusb_context libusb_context;
	typedef struct libusb_device libusb_device;

	/* USB Backend */
	b0_result_code b0_usb_open_vid_pid(b0_device **_dev, uint16_t vid, uint16_t pid);
	b0_result_code b0_usb_open(libusb_device *udevice, b0_device **_dev);
	b0_result_code b0_usb_open_handle(libusb_device_handle *uhandle, b0_device **_dev);
	b0_result_code b0_usb_open_supported(b0_device **dev);

	b0_result_code b0_usb_libusb_device_handle(b0_device *dev,
		libusb_device_handle **usbdh);
	b0_result_code b0_usb_libusb_context(b0_device *dev, libusb_context **usbc);
	b0_result_code b0_usb_libusb_device(b0_device *dev, libusb_device **usbd);

	b0_result_code b0_usb_device_bulk_timeout(b0_device *dev, unsigned timeout);
	b0_result_code b0_usb_device_ctrlreq_timeout(b0_device *dev, unsigned timeout);
	b0_result_code b0_usb_ain_iso_test(b0_ain *mod, bool enable);
	b0_result_code b0_usb_ain_iso_delay(b0_ain *mod, unsigned delay);
	b0_result_code b0_usb_aout_iso_test(b0_aout *mod, bool enable);
	b0_result_code b0_usb_aout_iso_pending(b0_aout *mod, unsigned iso_pending);

	/* ADXL345 */
	b0_result_code b0_adxl345_open_i2c(b0_i2c *mod, b0_adxl345 **drv, bool ALT_ADDRESS);
	b0_result_code b0_adxl345_close(b0_adxl345 *drv);
	b0_result_code b0_adxl345_read(b0_adxl345 *drv, double *x, double *y, double *z);
	b0_result_code b0_adxl345_info(b0_adxl345 *drv);
	b0_result_code b0_adxl345_power_up(b0_adxl345 *drv);

	/* H-Bridge */
	b0_result_code b0_hbridge_open(b0_dio *mod,
		b0_hbridge **drv, uint8_t EN, uint8_t A1, uint8_t A2);
	b0_result_code b0_hbridge_close(b0_hbridge *drv);
	b0_result_code b0_hbridge_info(b0_hbridge *drv);

	b0_result_code b0_hbridge_set(b0_hbridge *drv, int value);

	/* MCP342x */
	b0_result_code b0_mcp342x_open(b0_i2c *mod, b0_mcp342x **drv,
		b0_mcp342x_adr Adr1, b0_mcp342x_adr Adr0);
	b0_result_code b0_mcp342x_close(b0_mcp342x *drv);
	b0_result_code b0_mcp342x_info(b0_mcp342x *drv);
	b0_result_code b0_mcp342x_chan_set(b0_mcp342x *drv, b0_mcp342x_chan chan);
	b0_result_code b0_mcp342x_gain_set(b0_mcp342x *drv, b0_mcp342x_gain gain);
	b0_result_code b0_mcp342x_samp_rate_set(b0_mcp342x *drv,
		b0_mcp342x_samp_rate samp_rate);
	b0_result_code b0_mcp342x_read(b0_mcp342x *drv, double *value);

	/* ADS1220 */
	b0_result_code b0_ads1220_open(b0_spi *mod, b0_ads1220 **drv, uint8_t bSS);
	b0_result_code b0_ads1220_close(b0_ads1220 *drv);
	b0_result_code b0_ads1220_info(b0_ads1220 *drv);
	b0_result_code b0_ads1220_read(b0_ads1220 *drv, double *value);
	b0_result_code b0_ads1220_reset(b0_ads1220 *drv);
	b0_result_code b0_ads1220_start(b0_ads1220 *drv);
	b0_result_code b0_ads1220_power_down(b0_ads1220 *drv);
	b0_result_code b0_ads1220_gain_set(b0_ads1220 *drv, b0_ads1220_gain gain);
	b0_result_code b0_ads1220_pga_bypass_set(b0_ads1220 *drv, bool bypass);
	b0_result_code b0_ads1220_vref_set(b0_ads1220 *drv,
		b0_ads1220_vref_source source, double low, double high);
	b0_result_code b0_ads1220_filter_set(b0_ads1220 *drv, b0_ads1220_filter type);

	/* box-v5 */
	int b0_box0v5_ps_en_set(libusb_device_handle *usbdh, uint8_t mask, uint8_t value);
	int b0_box0v5_ps_en_get(libusb_device_handle *usbdh, uint8_t *value);
	int b0_box0v5_ps_oc_get(libusb_device_handle *usbdh, uint8_t *value);
	int b0_box0v5_ps_oc_ack(libusb_device_handle *usbdh, uint8_t mask);
""")

# https://bitbucket.org/cffi/cffi/issues/219
import sys
ext = "so" if sys.platform != "win32" else "dll"
libbox0 = ffi.dlopen("libbox0." + ext)

ffi.cdef("""size_t strlen(const char *);""")
libc = ffi.dlopen(None)

def string_converter(libbox0_str):
	"""
	convert *libbox0_str* to python string

	:param libbox_str: string buffer with utf-8 and NULL terimation
	:return: python unicode version of *libbox0_str*
	:rtype: str
	"""
	if libbox0_str == ffi.NULL:
		return None

	global libc
	buf = ffi.buffer(libbox0_str, libc.strlen(libbox0_str))
	return codecs.decode(buf, "utf-8")
