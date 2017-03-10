"""
<Program Name>
  test_director.py

<Purpose>
  Unit testing for uptane/services/director.py
  Also contains unittests of many functions in inventorydb.py

  Currently, running this test requires that the demo Director and demo OEM
  Repo be running.

"""
import os
import unittest

import shutil
import tuf
import uptane.services.inventorydb as inventory
import demo
import uptane
from uptane.services import director

TEST_DATA_DIR = os.path.join(uptane.WORKING_DIR, 'tests', 'test_data')
TEST_DIRECTOR_METADATA_DIR = os.path.join(TEST_DATA_DIR, 'director_metadata')
TEST_OEM_METADATA_DIR = os.path.join(TEST_DATA_DIR, 'oem_metadata')
TEST_DIRECTOR_ROOT_FNAME = os.path.join(TEST_DIRECTOR_METADATA_DIR, 'root.json')
TEST_OEM_ROOT_FNAME = os.path.join(TEST_OEM_METADATA_DIR, 'root.json')
TEST_PINNING_FNAME = os.path.join(TEST_DATA_DIR, 'pinned.json')

# Load what's necessary for the instantiation of a Director ECU, using
# valid things to start with.
director_repos_name = 'temp_test_director'

# I'll initialize this in one of the early tests, and use this for the simple
# non-damaging tests so as to avoid creating objects all over again.
director_instance = None

# Globally initialize these arguments of Director instance
director_repos_dir = None
key_root_pri = None
key_root_pub = None
key_timestamp_pri = None
key_timestamp_pub = None
key_snapshot_pri = None
key_snapshot_pub = None
key_targets_pri = None
key_targets_pub = None

# Some globals
ecu_manifests = {}
test_key_pri_ecu_pub = demo.import_public_key('primary')





def setUpModule():
    """
    This is run once for the full module, before all tests.
    It prepares some globals, including a single Director instance.
    """

    global key_root_pri
    global key_root_pub
    global key_timestamp_pri
    global key_timestamp_pub
    global key_snapshot_pri
    global key_snapshot_pub
    global key_targets_pri
    global key_targets_pub

    # Load the keys for Director
    key_root_pri = demo.import_private_key('directorroot')
    key_root_pub = demo.import_public_key('directorroot')
    key_timestamp_pri = demo.import_private_key('directortimestamp')
    key_timestamp_pub = demo.import_public_key('directortimestamp')
    key_snapshot_pri = demo.import_private_key('directorsnapshot')
    key_snapshot_pub = demo.import_public_key('directorsnapshot')
    key_targets_pri = demo.import_private_key('director')
    key_targets_pub = demo.import_public_key('director')

    if not os.path.exists(os.path.join(uptane.WORKING_DIR, director_repos_name)):
        os.mkdir(os.path.join(uptane.WORKING_DIR, director_repos_name))





def tearDownModule():
    if os.path.exists(os.path.join(uptane.WORKING_DIR, director_repos_name)):
        shutil.rmtree(os.path.join(uptane.WORKING_DIR, director_repos_name))
    pass





class TestDirector(unittest.TestCase):
    """
    "unittest"-style test class for the Director module in the reference
    implementation

    Please note that these tests are NOT entirely independent of each other.
    Several of them build on the results of previous tests. This is an unusual
    pattern but saves code and works at least for now.
    """

    def test_01_initial(self):
        global director_instance

        # Now try creating a Director with a series of bad arguments, expecting
        # errors.

        # Invalid private root key:
        with self.assertRaises(tuf.FormatError):
            d = director.Director(
                director_repos_dir=os.path.join(uptane.WORKING_DIR, director_repos_name),
                key_root_pri='',
                key_root_pub=key_root_pub,
                key_timestamp_pri=key_timestamp_pri,
                key_timestamp_pub=key_timestamp_pub,
                key_snapshot_pri=key_snapshot_pri,
                key_snapshot_pub=key_snapshot_pub,
                key_targets_pri=key_targets_pri,
                key_targets_pub=key_targets_pub
            )

        # Invalid public root key:
        with self.assertRaises(tuf.FormatError):
            d = director.Director(
                director_repos_dir=os.path.join(uptane.WORKING_DIR, director_repos_name),
                key_root_pri=key_root_pri,
                key_root_pub='',
                key_timestamp_pri=key_timestamp_pri,
                key_timestamp_pub=key_timestamp_pub,
                key_snapshot_pri=key_snapshot_pri,
                key_snapshot_pub=key_snapshot_pub,
                key_targets_pri=key_targets_pri,
                key_targets_pub=key_targets_pub
            )

        # Invalid private timestamp key:
        with self.assertRaises(tuf.FormatError):
            d = director.Director(
                director_repos_dir=os.path.join(uptane.WORKING_DIR, director_repos_name),
                key_root_pri=key_root_pri,
                key_root_pub=key_root_pub,
                key_timestamp_pri='',
                key_timestamp_pub=key_timestamp_pub,
                key_snapshot_pri=key_snapshot_pri,
                key_snapshot_pub=key_snapshot_pub,
                key_targets_pri=key_targets_pri,
                key_targets_pub=key_targets_pub
            )

        # Invalid public timestamp key:
        with self.assertRaises(tuf.FormatError):
            d = director.Director(
                director_repos_dir=os.path.join(uptane.WORKING_DIR, director_repos_name),
                key_root_pri=key_root_pri,
                key_root_pub=key_root_pub,
                key_timestamp_pri=key_timestamp_pri,
                key_timestamp_pub='',
                key_snapshot_pri=key_snapshot_pri,
                key_snapshot_pub=key_snapshot_pub,
                key_targets_pri=key_targets_pri,
                key_targets_pub=key_targets_pub
            )

        # Invalid private snapshot key:
        with self.assertRaises(tuf.FormatError):
            d = director.Director(
                director_repos_dir=os.path.join(uptane.WORKING_DIR, director_repos_name),
                key_root_pri=key_root_pri,
                key_root_pub=key_root_pub,
                key_timestamp_pri=key_timestamp_pri,
                key_timestamp_pub=key_timestamp_pub,
                key_snapshot_pri='',
                key_snapshot_pub=key_snapshot_pub,
                key_targets_pri=key_targets_pri,
                key_targets_pub=key_targets_pub
            )

        # Invalid public snapshot key:
        with self.assertRaises(tuf.FormatError):
            d = director.Director(
                director_repos_dir=os.path.join(uptane.WORKING_DIR, director_repos_name),
                key_root_pri=key_root_pri,
                key_root_pub=key_root_pub,
                key_timestamp_pri=key_timestamp_pri,
                key_timestamp_pub=key_timestamp_pub,
                key_snapshot_pri=key_snapshot_pri,
                key_snapshot_pub='',
                key_targets_pri=key_targets_pri,
                key_targets_pub=key_targets_pub
            )

        # Invalid private targets key:
        with self.assertRaises(tuf.FormatError):
            d = director.Director(
                director_repos_dir=os.path.join(uptane.WORKING_DIR, director_repos_name),
                key_root_pri=key_root_pri,
                key_root_pub=key_root_pub,
                key_timestamp_pri=key_timestamp_pri,
                key_timestamp_pub=key_timestamp_pub,
                key_snapshot_pri=key_snapshot_pri,
                key_snapshot_pub=key_snapshot_pub,
                key_targets_pri='',
                key_targets_pub=key_targets_pub
            )

        # Invalid public targets key:
        with self.assertRaises(tuf.FormatError):
            d = director.Director(
                director_repos_dir=os.path.join(uptane.WORKING_DIR, director_repos_name),
                key_root_pri=key_root_pri,
                key_root_pub=key_root_pub,
                key_timestamp_pri=key_timestamp_pri,
                key_timestamp_pub=key_timestamp_pub,
                key_snapshot_pri=key_snapshot_pri,
                key_snapshot_pub=key_snapshot_pub,
                key_targets_pri=key_targets_pri,
                key_targets_pub=''
            )

        # Try creating a Director, expecting it to work.
        # Initializes a Director Instance
        director_instance = director.Director(
            director_repos_dir=os.path.join(uptane.WORKING_DIR, director_repos_name),
            key_root_pri=key_root_pri,
            key_root_pub=key_root_pub,
            key_timestamp_pri=key_timestamp_pri,
            key_timestamp_pub=key_timestamp_pub,
            key_snapshot_pri=key_snapshot_pri,
            key_snapshot_pub=key_snapshot_pub,
            key_targets_pri=key_targets_pri,
            key_targets_pub=key_targets_pub
        )

        # Check the fields initialized in the instance to make sure they're correct.
        self.assertEqual(os.path.join(uptane.WORKING_DIR, director_repos_name), director_instance.director_repos_dir)
        self.assertEqual(key_root_pri, director_instance.key_dirroot_pri)
        self.assertEqual(key_root_pub, director_instance.key_dirroot_pub)
        self.assertEqual(key_timestamp_pri, director_instance.key_dirtime_pri)
        self.assertEqual(key_timestamp_pub, director_instance.key_dirtime_pub)
        self.assertEqual(key_snapshot_pri, director_instance.key_dirsnap_pri)
        self.assertEqual(key_snapshot_pub, director_instance.key_dirsnap_pub)
        self.assertEqual(key_targets_pri, director_instance.key_dirtarg_pri)
        self.assertEqual(key_targets_pub, director_instance.key_dirtarg_pub)
        self.assertEqual({}, director_instance.vehicle_repositories)






    def test_05_add_new_vehicle(self):
        global director_instance

        self.assertEqual({}, inventory.ecus_by_vin)
        director_instance.add_new_vehicle('111')
        self.assertIn('111', inventory.ecus_by_vin)





    def test_10_create_director_repo_for_vehicle(self):
        global director_instance

        # Check whether there is corresponding directory of the newly add vehicle
        self.assertTrue(os.path.exists(os.path.join(director_instance.director_repos_dir, '111')))
        temp_dir = os.path.join(director_instance.director_repos_dir, '111')
        print("Angelina + " + temp_dir)
        self.assertTrue(os.path.exists(os.path.join(temp_dir, tuf.repository_tool.METADATA_STAGED_DIRECTORY_NAME)))
        self.assertTrue(os.path.exists(os.path.join(temp_dir, tuf.repository_tool.TARGETS_DIRECTORY_NAME)))

        # Check whether there is a correct tuf object
        self.assertIsNotNone(director_instance.vehicle_repositories['111'])
        self.assertIsInstance(director_instance.vehicle_repositories['111'], tuf.repository_tool.Repository)

        # TODO: Do we need to continue checking the key of this Repository object.
        # I think it's the work of the TUF test so I don't check it again here





    def test_15_add_target_for_ecu(self):
        global director_instance

        # First copy a target file into test directory
        test_vin = '111'
        test_ecu_serial = '00000'
        source_target_file = os.path.join(demo.MAIN_REPO_TARGETS_DIR, 'infotainment_firmware.txt')
        dest_target_file = os.path.join(director_instance.director_repos_dir, test_vin)
        dest_target_file = os.path.join(dest_target_file, 'targets')
        print ('Felix dest_target_file' + dest_target_file)
        shutil.copy(source_target_file, dest_target_file)
        final_file = os.path.join(dest_target_file, 'infotainment_firmware.txt')

        director_instance.add_target_for_ecu(test_vin, test_ecu_serial, final_file)

        self.assertIsNotNone(director_instance.vehicle_repositories[test_vin].targets)

        # TODO:Need more specific test of TUF Repository Object
        # roleinfo = tuf.roledb.get_roleinfo(director_instance.vehicle_repositories[test_vin].targets._rolename)
        # relative_path = filepath[targets_directory_length:]
        # tuf.roledb.update_roleinfo(self._rolename, roleinfo)
        # self.assertIn('infotainment_firmware.txt', roleinfo['paths'])
        # self.assertEqual(director_instance.vehicle_repositories[test_vin]['targets'], 'infotainment_firmware.txt')
        # self.assertEqual(director_instance.vehicle_repositories[test_vin].targets['customs'], '00000')

        self.assertTrue(os.path.exists(final_file))





    def test_20_register_ecu_serial(self):
        global director_instance

        test_vin = '111'
        test_pri_ecu_serial = '00000'
        test_key_pri_ecu_pub = demo.import_public_key('primary')
        test_non_pri_ecu_serial = '11111'
        test_non_pri_key_ecu_pub = demo.import_public_key('secondary')

        # If vin is unknown
        with self.assertRaises(uptane.UnknownVehicle):
            director_instance.register_ecu_serial(test_pri_ecu_serial, test_key_pri_ecu_pub, '112', is_primary=False)

        # Register a correct primary ecu
        director_instance.register_ecu_serial(test_pri_ecu_serial, test_key_pri_ecu_pub, test_vin, is_primary=True)
        self.assertIn(test_pri_ecu_serial, inventory.ecus_by_vin['111'])
        self.assertIn(test_pri_ecu_serial, inventory.primary_ecus_by_vin['111'])
        self.assertEqual(test_key_pri_ecu_pub, inventory.ecu_public_keys['00000'])

        # Register a correct non-primary ecu
        director_instance.register_ecu_serial(test_non_pri_ecu_serial, test_non_pri_key_ecu_pub, test_vin,
                                              is_primary=False)
        self.assertIn(test_non_pri_ecu_serial, inventory.ecus_by_vin['111'])
        self.assertNotIn(test_non_pri_ecu_serial, inventory.primary_ecus_by_vin['111'])
        self.assertEqual(test_non_pri_key_ecu_pub, inventory.ecu_public_keys['11111'])

        # Register a duplicate primary ecu
        with self.assertRaises(uptane.Spoofing):
            director_instance.register_ecu_serial(test_non_pri_ecu_serial, test_non_pri_key_ecu_pub, test_vin,
                                                  is_primary=True)





    def test_25_register_vehicle_manifest(self):

        """
        Also contains the test of directory.validate_primary_certification_in_vehicle_manifest()

        :return:
        """
        global director_instance

        # Create the vv manifest:
        # Note: only vin and ecu_serial is meaningful
        test_signed_vehicle_manifest = {
            'signatures': [
                {
                    'keyid': '9a406d99e362e7c93e7acfe1e4d6585221315be817f350c026bbee84ada260da',
                    'sig': 'ab04e6f2efdaec7bdf4ec32d57e66454e5f94695f0dfe631b68139789323e6c6ec7d8e805fa9be4a52bae32706cb532e846b0665608974b9a749a5def4521c00',
                    'method': 'ed25519'
                }
            ],
            'signed': {
                'ecu_version_manifests': {
                    '22222': [
                        {
                            'signatures': [
                                {
                                    'keyid': '49309f114b857e4b29bfbff1c1c75df59f154fbc45539b2eb30c8a867843b2cb',
                                    'sig': 'c19a6a2738f9f6fb46a5e7af96649db8f247d05863ba056fa6e2bb27b6aafdffd885845cffe89f036b5ed51473b23ba7abec79865c4866f83893e2bb805ad104',
                                    'method': 'ed25519'
                                }
                            ],
                            'signed': {
                                'previous_timeserver_time': '2017-03-03T17:16:30Z',
                                'timeserver_time': '2017-03-03T17:16:30Z',
                                'ecu_serial': '22222',
                                'installed_image': {
                                    'fileinfo': {
                                        'hashes': {
                                            'sha256': '6b9f987226610bfed08b824c93bf8b2f59521fce9a2adef80c495f363c1c9c44',
                                            'sha512': '706c283972c5ae69864b199e1cdd9b4b8babc14f5a454d0fd4d3b35396a04ca0b40af731671b74020a738b5108a78deb032332c36d6ae9f31fae2f8a70f7e1ce'
                                        },
                                        'length': 37
                                    },
                                    'filepath': '/secondary_firmware.txt'
                                },
                                'attacks_detected': ''
                            }
                        }
                    ]
                },
                'primary_ecu_serial': '11111',
                'vin': '111'
            }
        }

        # Create a wrong one
        test_wrong_signed_vehicle_manifest = {
            'signatures': [
                {
                    'keyid': '9a406d99e362e7c93e7acfe1e4d6585221315be817f350c026bbee84ada260da',
                    'sig': 'ab04e6f2efdaec7bdf4ec32d57e66454e5f94695f0dfe631b68139789323e6c6ec7d8e805fa9be4a52bae32706cb532e846b0665608974b9a749a5def4521c00',
                    'method': 'ed25519'
                }
            ],
            'signed': {
                'ecu_version_manifests': {
                    '22222': [
                        {
                            'signatures': [
                                {
                                    'keyid': '49309f114b857e4b29bfbff1c1c75df59f154fbc45539b2eb30c8a867843b2cb',
                                    'sig': 'c19a6a2738f9f6fb46a5e7af96649db8f247d05863ba056fa6e2bb27b6aafdffd885845cffe89f036b5ed51473b23ba7abec79865c4866f83893e2bb805ad104',
                                    'method': 'ed25519'
                                }
                            ],
                            'signed': {
                                'previous_timeserver_time': '2017-03-03T17:16:30Z',
                                'timeserver_time': '2017-03-03T17:16:30Z',
                                'ecu_serial': '22222',
                                'installed_image': {
                                    'fileinfo': {
                                        'hashes': {
                                            'sha256': '6b9f987226610bfed08b824c93bf8b2f59521fce9a2adef80c495f363c1c9c44',
                                            'sha512': '706c283972c5ae69864b199e1cdd9b4b8babc14f5a454d0fd4d3b35396a04ca0b40af731671b74020a738b5108a78deb032332c36d6ae9f31fae2f8a70f7e1ce'
                                        },
                                        'length': 37
                                    },
                                    'filepath': '/secondary_firmware.txt'
                                },
                                'attacks_detected': ''
                            }
                        }
                    ]
                },
                'primary_ecu_serial': '33333',
                'vin': '111'
            }
        }

        # Now we try to register such a vehicle manifest
        # Check if the vin is unknown
        with self.assertRaises(uptane.UnknownVehicle):
            director_instance.register_vehicle_manifest('113', '11111', test_signed_vehicle_manifest)

        # The following three cases actually test the function of 'director.validate_primary_certification_in_vehicle_manifest'
        # Check if the primary_ecu_serial is not the same with the one in the manifest
        with self.assertRaises(uptane.Spoofing):
            director_instance.register_vehicle_manifest('111', '00000', test_signed_vehicle_manifest)

        # Check if the ecu hasn't been registered
        with self.assertRaises(uptane.UnknownECU):
            director_instance.register_vehicle_manifest('111', '33333', test_wrong_signed_vehicle_manifest)


        test_bad_sig_signed_vehicle_manifest = {
            'signatures': [
                {
                    'keyid': '9a406d99e362e7c93e7acfe1e4d6585221315be817f350c026bbee84ada260da',
                    'sig': 'badsignature',
                    'method': 'ed25519'
                }
            ],
            'signed': {
                'ecu_version_manifests': {
                    '22222': [
                        {
                            'signatures': [
                                {
                                    'keyid': '49309f114b857e4b29bfbff1c1c75df59f154fbc45539b2eb30c8a867843b2cb',
                                    'sig': 'c19a6a2738f9f6fb46a5e7af96649db8f247d05863ba056fa6e2bb27b6aafdffd885845cffe89f036b5ed51473b23ba7abec79865c4866f83893e2bb805ad104',
                                    'method': 'ed25519'
                                }
                            ],
                            'signed': {
                                'previous_timeserver_time': '2017-03-03T17:16:30Z',
                                'timeserver_time': '2017-03-03T17:16:30Z',
                                'ecu_serial': '22222',
                                'installed_image': {
                                    'fileinfo': {
                                        'hashes': {
                                            'sha256': '6b9f987226610bfed08b824c93bf8b2f59521fce9a2adef80c495f363c1c9c44',
                                            'sha512': '706c283972c5ae69864b199e1cdd9b4b8babc14f5a454d0fd4d3b35396a04ca0b40af731671b74020a738b5108a78deb032332c36d6ae9f31fae2f8a70f7e1ce'
                                        },
                                        'length': 37
                                    },
                                    'filepath': '/secondary_firmware.txt'
                                },
                                'attacks_detected': ''
                            }
                        }
                    ]
                },
                'primary_ecu_serial': '11111',
                'vin': '111'
            }
        }

        # Check if the signature is wrong
        # This error actually will be captured by Format check in 'register_vehicle_manifest'
        with self.assertRaises(tuf.FormatError):
            director_instance.register_vehicle_manifest('111', '11111', test_bad_sig_signed_vehicle_manifest)

        # TODO: Do a correct register
        # Don't know why there's always a bad signature error
        # director_instance.register_vehicle_manifest('111', '11111', test_signed_vehicle_manifest)
        #
        # # Check if the inventory has saved
        # self.assertIn(test_signed_vehicle_manifest, inventory.vehicle_manifests['111'])





    def test_30_add_target_for_ecu(self):

        global director_instance

        # Check if is an unknown vehicle
        with self.assertRaises(uptane.UnknownVehicle):
            director_instance.add_target_for_ecu('113', '11111', '/Users/Felix/virtualEnv/Uptane/bin/uptane/temp_test_director/111/targets/infotainment_firmware.txt')

        # Add reasonable targets
        director_instance.add_target_for_ecu('111', '11111', '/Users/Felix/virtualEnv/Uptane/bin/uptane/temp_test_director/111/targets/infotainment_firmware.txt')

        # TODO: Need more specific test of TUF Repository Object
        # roleinfo = tuf.roledb.get_roleinfo(director_instance.vehicle_repositories[test_vin].targets._rolename)
        # relative_path = filepath[targets_directory_length:]
        # tuf.roledb.update_roleinfo(self._rolename, roleinfo)
        # self.assertIn('infotainment_firmware.txt', roleinfo['paths'])





if __name__ == '__main__':
    unittest.main()