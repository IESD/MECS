import uuid
import logging

from .. import config_file

log = logging.getLogger(__name__)

def write_identifier(conf, force=False):
    """write unique identifier into config file"""
    if force or ("data_acquisition_id" not in conf['MECS']):
        identifier = hex(uuid.getnode())
        conf.set('MECS', 'data_acquisition_id', identifier)
        path = config_file()
        with open(path, 'w') as f:
            conf.write(f)
        log.info(f"New data_acquisition_id based on MAC address: {identifier}")
    else:
        log.info(f"Existing data_acquisition_id: {conf['MECS']['data_acquisition_id']}")
