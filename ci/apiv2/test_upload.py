#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# PoC testing/development framework for APIv2 upload TUS
#
# Nice helper: $sudo justniffer -i lo -r
import unittest
import datetime
import logging
from io import BytesIO


import tusclient.client

import utils

#logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Files(utils.TestBase):
    def getBaseURI(self):
        return '/ui/files/import'
        
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Remove preset 'Content-Type' header, since this will bork the file uploader
        del cls._headers['Content-Type']


    def do_upload(self, filename):
        uri = self.getURI()

        my_client = tusclient.client.TusClient(uri)
        my_client.set_headers(self._headers)
        
        N = 1000
        #res = ''.join(random.choices(string.ascii_uppercase + string.digits, k=N))
        res = '\n'.join([f'Line-{i}' for i in range(N)])
        fs = BytesIO(res.encode('UTF-8'))
        metadata = {"filename": filename,
                    "filetype": "application/text"}
        uploader = my_client.uploader(
                file_stream=fs,
                chunk_size=4000,
                upload_checksum=True,
                metadata=metadata
                )
        logger.debug(uploader.get_headers())
        logger.debug(uploader.encode_metadata())
        uploader.upload()
        logger.debug(vars(uploader))
        self.assertEqual(uploader.stop_at, uploader.offset)


    def test_upload(self):
        stamp = datetime.datetime.now().isoformat()
        filename = f"test_upload_{stamp}.csv"
        self.do_upload(filename)


    def test_upload_existing_file(self):
        stamp = datetime.datetime.now().isoformat()
        filename = f"test_existing_file_upload_{stamp}.csv"
        self.do_upload(filename)

        # Try uploading again
        with self.assertRaises(tusclient.exceptions.TusCommunicationError) as cm:
            self.do_upload(filename)
        self.assertEqual(cm.exception.status_code, 400)
            

if __name__ == '__main__':
    unittest.main()
