import logging

# configure the logger when using the supplied examples, as opposed to running as a library
# called from an external program (which then should take care of configuring the logging)
def configure_default_logger(is_verbose_enabled):
  log = logging.getLogger()
  formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
  handler = logging.StreamHandler()
  handler.setFormatter(formatter)
  log.addHandler(handler)
  log.setLevel(logging.INFO)
  if is_verbose_enabled:
    log.setLevel(logging.DEBUG)