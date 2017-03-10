"""
<Program Name>
  test_secondary.py

<Purpose>
  Unit testing for uptane/clients/secondary.py

  Currently, running this test requires that the demo Director and demo OEM
  Repo be running.

"""
from __future__ import unicode_literals

import zipfile

import uptane
import uptane.formats
import uptane.clients.secondary as secondary
import uptane.common
import tuf
import tuf.formats
import tuf.client.updater # to test one of the fields in the Secondary object
import tuf.keys # to validate a signature

import unittest
import os.path
import time
import copy
import shutil

# For temporary convenience:
import demo # for generate_key, import_public_key, import_private_key

TEST_DATA_DIR = os.path.join(uptane.WORKING_DIR, 'tests', 'test_data')
TEST_DIRECTOR_METADATA_DIR = os.path.join(TEST_DATA_DIR, 'director_metadata')
TEST_OEM_METADATA_DIR = os.path.join(TEST_DATA_DIR, 'oem_metadata')
TEST_DIRECTOR_ROOT_FNAME = os.path.join(TEST_DIRECTOR_METADATA_DIR, 'root.json')
TEST_OEM_ROOT_FNAME = os.path.join(TEST_OEM_METADATA_DIR, 'root.json')
TEST_PINNING_FNAME = os.path.join(TEST_DATA_DIR, 'pinned.json')

# I'll initialize this in one of the early tests, and use this for the simple
# non-damaging tests so as to avoid creating objects all over again.
secondary_instance = None

# Changing some of these values would require producing new signed sample data
# from the Timeserver or a Secondary.
nonce = 5
vin = '000'
ecu_serial = '00000'

last_nonce_sent = None
nonce_next = None

# Load what's necessary for the instantiation of a Secondary ECU, using
# valid things to start with.
client_directory_name = 'temp_test_secondary'

# Initialize these in setUpModule below.
secondary_ecu_key = None
key_timeserver_pub = None
clock = None
process_timeserver = None
process_director = None
process_oemrepo = None
firmware_fileinfo = None
director_public_key = None
# Set starting firmware fileinfo (that this ECU had coming from the factory)
factory_firmware_fileinfo = {
    'filepath': '/secondary_firmware.txt',
    'fileinfo': {
        'hashes': {
            'sha512': '706c283972c5ae69864b199e1cdd9b4b8babc14f5a454d0fd4d3b35396a04ca0b40af731671b74020a738b5108a78deb032332c36d6ae9f31fae2f8a70f7e1ce',
            'sha256': '6b9f987226610bfed08b824c93bf8b2f59521fce9a2adef80c495f363c1c9c44'},
        'length': 37}}



def destroy_temp_dir():
  # Clean up anything that may currently exist in the temp test directory.
  if os.path.exists(os.path.join(TEST_DATA_DIR, client_directory_name)):
    shutil.rmtree(os.path.join(TEST_DATA_DIR, client_directory_name))





def setUpModule():
  """
  This is run once for the full module, before all tests.
  It prepares some globals, including a single Secondary ECU client instance.
  When finished, it will also start up an OEM Repository Server,
  Director Server, and Time Server. Currently, it requires them to be already
  running.
  """
  # global secondary_ecu_key
  global secondary_ecu_key
  global key_timeserver_pub
  global clock
  global firmware_fileinfo
  global director_public_key
  destroy_temp_dir()

  # Load the private key for this Secondary ECU.
  key_pub = demo.import_public_key('secondary')
  key_pri = demo.import_private_key('secondary')
  secondary_ecu_key = uptane.common.canonical_key_from_pub_and_pri(
      key_pub, key_pri)

  # Load the public timeserver key.
  key_timeserver_pub = demo.import_public_key('timeserver')

  # # Load the public director key.
  # director_public_key = demo.import_public_key('director')

  # Generate a trusted initial time for the Secondary.
  clock = tuf.formats.unix_timestamp_to_datetime(int(time.time()))
  clock = clock.isoformat() + 'Z'
  tuf.formats.ISO8601_DATETIME_SCHEMA.check_match(clock)

  # Create a firmware file
  firmware_fileinfo = {}

  # Currently in development.

  # Start the timeserver, director, and oem repo for this test,
  # using subprocesses, and saving those processes as:
  #process_timeserver
  #process_director
  #process_oemrepo
  # to be stopped in tearDownModule below.





def tearDownModule():
  """This is run once for the full module, after all tests."""
  destroy_temp_dir()





class TestSecondary(unittest.TestCase):
  """
  "unittest"-style test class for the Secondary module in the reference
  implementation

  Please note that these tests are NOT entirely independent of each other.
  Several of them build on the results of previous tests. This is an unusual
  pattern but saves code and works at least for now.
  """

  def test_01_init(self):
    """
    Note that this doesn't test the root files provided, as those aren't used
    at all in the initialization; for that, we'll have to test the update cycle.
    """

    # global secondary_instance
    global secondary_instance


    # Set up a client directory first.
    uptane.common.create_directory_structure_for_client(
        client_directory_name,
        TEST_PINNING_FNAME,
        {'mainrepo': TEST_OEM_ROOT_FNAME,
        'director': TEST_DIRECTOR_ROOT_FNAME})

    # Director repo not specified in pinning file
    # TODO: Same comment as above: need to edit the pinning file on disk for
    # this test to work.
    # with self.assertRaises(uptane.Error):
    #     s = secondary.Secondary(
    #         full_client_dir=os.path.join(TEST_DATA_DIR, client_directory_name),
    #         pinning_filename=TEST_PINNING_FNAME,
    #         director_repo_name='this_is_not_the_name_of_any_repository',
    #         vin=vin,
    #         ecu_serial=ecu_serial,
    #         ecu_key=secondary_ecu_key,
    #         time=clock,
    #         timeserver_public_key=key_timeserver_pub,
    #         firmware_fileinfo=firmware_fileinfo,
    #         director_public_key=director_public_key,
    #         partial_verifying=False)

    # Invalid VIN:
    with self.assertRaises(tuf.FormatError):
        s = secondary.Secondary(
            full_client_dir=os.path.join(TEST_DATA_DIR, client_directory_name),
            director_repo_name=demo.DIRECTOR_REPO_NAME,
            vin=5,
            ecu_serial=ecu_serial,
            ecu_key=secondary_ecu_key,
            time=clock,
            timeserver_public_key=key_timeserver_pub,
            firmware_fileinfo=factory_firmware_fileinfo,
            director_public_key=director_public_key,
            partial_verifying=False)

    # Invalid ECU Serial:
    with self.assertRaises(tuf.FormatError):
        s = secondary.Secondary(
            full_client_dir=os.path.join(TEST_DATA_DIR, client_directory_name),
            director_repo_name=demo.DIRECTOR_REPO_NAME,
            vin=vin,
            ecu_serial=500,
            ecu_key=secondary_ecu_key,
            time=clock,
            timeserver_public_key=key_timeserver_pub,
            firmware_fileinfo=factory_firmware_fileinfo,
            director_public_key=director_public_key,
            partial_verifying=False)

    # Invalid ECU Key:
    with self.assertRaises(tuf.FormatError):
        s = secondary.Secondary(
            full_client_dir=os.path.join(TEST_DATA_DIR, client_directory_name),
            director_repo_name=demo.DIRECTOR_REPO_NAME,
            vin=vin,
            ecu_serial=ecu_serial,
            ecu_key={''},
            time=clock,
            timeserver_public_key=key_timeserver_pub,
            firmware_fileinfo=firmware_fileinfo,
            director_public_key=director_public_key,
            partial_verifying=False)

    # Invalid time:
    with self.assertRaises(tuf.FormatError):
        s = secondary.Secondary(
            full_client_dir=os.path.join(TEST_DATA_DIR, client_directory_name),
            director_repo_name=demo.DIRECTOR_REPO_NAME,
            vin=vin,
            ecu_serial=ecu_serial,
            ecu_key=secondary_ecu_key,
            time='potato',
            timeserver_public_key=key_timeserver_pub,
            firmware_fileinfo=factory_firmware_fileinfo,
            director_public_key=director_public_key,
            partial_verifying=False)

    # # Invalid firmware_fileinfo:
    # TODO: I think we should check the firmware_fileinfo in secondary.init()
    # with self.assertRaises(tuf.FormatError):
    #     s = secondary.Secondary(
    #         full_client_dir=os.path.join(TEST_DATA_DIR, client_directory_name),
    #         director_repo_name=demo.DIRECTOR_REPO_NAME,
    #         vin=vin,
    #         ecu_serial=ecu_serial,
    #         ecu_key=secondary_ecu_key,
    #         time=clock,
    #         timeserver_public_key=key_timeserver_pub,
    #         firmware_fileinfo='potato',
    #         director_public_key=director_public_key,
    #         partial_verifying=False)

    # Invalid directory_public_key:
    with self.assertRaises(tuf.FormatError):
        s = secondary.Secondary(
            full_client_dir=os.path.join(TEST_DATA_DIR, client_directory_name),
            director_repo_name=demo.DIRECTOR_REPO_NAME,
            vin=vin,
            ecu_serial=ecu_serial,
            ecu_key=secondary_ecu_key,
            time=clock,
            timeserver_public_key=key_timeserver_pub,
            firmware_fileinfo=factory_firmware_fileinfo,
            director_public_key={''},
            partial_verifying=False)

    # Try creating a Secondary, expecting it to work.
    # Initializes a Secondary ECU, making a client directory and copying the root
    # file from the repositories.
    # Save the result for future tests, to save time and code.
    # TODO: Stick TEST_PINNING_FNAME in the right place.
    # Stick TEST_OEM_ROOT_FNAME and TEST_DIRECTOR_ROOT_FNAME in the right place.
    secondary_instance = secondary.Secondary(
        full_client_dir=os.path.join(TEST_DATA_DIR, client_directory_name),
        director_repo_name=demo.DIRECTOR_REPO_NAME,
        vin=vin,
        ecu_serial=ecu_serial,
        ecu_key=secondary_ecu_key,
        time=clock,
        timeserver_public_key=key_timeserver_pub,
        firmware_fileinfo=factory_firmware_fileinfo,
        director_public_key=None,
        partial_verifying=False)

    # Check the fields initialized in the instance to make sure they're correct.

    self.assertEqual(None, secondary_instance.last_nonce_sent)
    self.assertEqual(vin, secondary_instance.vin)
    self.assertEqual(ecu_serial, secondary_instance.ecu_serial)
    self.assertEqual(secondary_ecu_key, secondary_instance.ecu_key)
    self.assertEqual(director_public_key, secondary_instance.director_public_key)
    self.assertEqual(
        secondary_instance.full_client_dir, os.path.join(TEST_DATA_DIR, client_directory_name))
    self.assertEqual(factory_firmware_fileinfo, secondary_instance.firmware_fileinfo)
    self.assertEqual([clock, clock], secondary_instance.all_valid_timeserver_times)
    self.assertIsInstance(secondary_instance.updater, tuf.client.updater.Updater)
    tuf.formats.ANYKEY_SCHEMA.check_match(secondary_instance.timeserver_public_key)





  def test_05_generate_signed_ecu_manifest(self):
      global secondary_instance

      # Create an empty description_of_attacks_observed for future test and check its format everytime
      description_of_attacks_observed = ''
      uptane.formats.DESCRIPTION_OF_ATTACKS_SCHEMA.check_match(
          description_of_attacks_observed)

      signed_ecu_manifest = secondary_instance.generate_signed_ecu_manifest()

      # Test format of ecu_manifest
      uptane.formats.SIGNABLE_ECU_VERSION_MANIFEST_SCHEMA.check_match(
          signed_ecu_manifest)

      # Test contents of ecu manifest.
      # Make sure there is exactly one signature.
      self.assertEqual(1, len(signed_ecu_manifest['signatures']))

      # TODO: More testing of the contents of the vehicle manifest.

      # Check the signature on the ecu manifest.
      self.assertTrue(tuf.keys.verify_signature(
          secondary_ecu_key,
          signed_ecu_manifest['signatures'][0],  # TODO: Fix assumptions.
          signed_ecu_manifest['signed']))





  def test_10_set_nonce_as_sent(self):
      global secondary_instance

      secondary_instance.nonce_next = secondary_instance._create_nonce()
      secondary_instance.set_nonce_as_sent()

      # Test if last_nonce_sent is not None
      self.assertIsNotNone(secondary_instance.last_nonce_sent)

      # Test if nonce_next is not None
      self.assertIsNotNone(secondary_instance.nonce_next)

      # Test if last_nonce_sent is equal to nonce_next
      self.assertEqual(secondary_instance.nonce_next, secondary_instance.last_nonce_sent)





  def test_15_validate_time_attestation(self):
      global secondary_instance

      # Try a valid time attestation first, signed by an expected timeserver key,
      # with an expected nonce (previously "received" from a Secondary)
      secondary_instance.last_nonce_sent = nonce
      time_attestation = {
          'signed': {'nonces': [nonce], 'time': '2016-11-02T21:06:05Z'},
          'signatures': [{
            'method': 'ed25519',
            'sig': 'aabffcebaa57f1d6397bdc5647764261fd23516d2996446c3c40b3f30efb2a4a8d80cd2c21a453e78bf99dafb9d0f5e56c4e072db365499fa5f2f304afec100e',
            'keyid': '79c796d7e87389d1ebad04edce49faef611d139ee41ea9fb1931732afbfaac2e'}]}

      secondary_instance.validate_time_attestation(time_attestation)

      # Test the new time is in the all_valid_timeserver_times
      new_time = time_attestation['signed']['time']
      self.assertIn(new_time, secondary_instance.all_valid_timeserver_times)

      # Test the new nonce is changed
      self.assertNotEqual(secondary_instance.nonce_next, nonce)

      # Try again with part of the signature replaced.
      time_attestation__badsig = copy.deepcopy(time_attestation)
      time_attestation__badsig['signatures'][0]['sig'] = '987654321' + \
                                                         time_attestation__badsig['signatures'][0]['sig'][9:]

      with self.assertRaises(tuf.BadSignatureError):
          secondary_instance.validate_time_attestation(time_attestation__badsig)

      with self.assertRaises(uptane.BadTimeAttestation):
          self.assertNotEqual(500, nonce, msg='Programming error: bad and good '
                                              'test nonces are equal.')

          time_attestation__wrongnonce = {
              'signed': {'nonces': [500], 'time': '2016-11-02T21:15:00Z'},
              'signatures': [{
                  'method': 'ed25519',
                  'sig': '4d01df35ca829fd7ead1408c250950c444db8ac51fa929a7f0288578fbf81016f0e81ed35789689481aee6b7af28ab311306397ef38572732854fb6cf2072604',
                  'keyid': '79c796d7e87389d1ebad04edce49faef611d139ee41ea9fb1931732afbfaac2e'}]}

          secondary_instance.validate_time_attestation(time_attestation__wrongnonce)





  def test_20_process_metadata(self):
      """
      Also contains the test of secondary._expand_metadata_archive()
      :return:
      """
      global secondary_instance

      archive_fname = os.path.join(
          uptane.WORKING_DIR, client_directory_name, 'metadata_archive.zip')

      # Just use the pinned.json as an example for test
      f = zipfile.ZipFile(archive_fname, 'w', zipfile.ZIP_DEFLATED)
      f.write(os.path.join(uptane.WORKING_DIR, client_directory_name, 'metadata', 'pinned.json'))
      f.close()

      # Check if the archive doesn't exist
      with self.assertRaises(uptane.Error):
          secondary_instance.process_metadata("/test_archive.zip")

      # Do a correct process_metadata
      secondary_instance.process_metadata(archive_fname)

      # Check if there's extracted file
      self.assertTrue(os.path.exists(os.path.join(secondary_instance.full_client_dir, 'unverified')))

      # TODO:There should also be the test for secondary.fully_validate_metadata and secondary.get_validated_target_info
      # But because there are no valid targets in current metadata, the test cannot be done





  def test_25_validate_image(self):

      #TODO:Same reason above. No enough data for test now.
      pass





# Run unit test.
if __name__ == '__main__':
  unittest.main()