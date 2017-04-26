from unittest import TestCase

from cloudshell.networking.juniper.helpers.add_remove_vlan_helper import VlanRange, VlanRangeOperations


class TestVlanRange(TestCase):
    def setUp(self):
        pass

    def test_init(self):
        first_id = '20'
        last_id = '50'
        instance = VlanRange((first_id, last_id))
        self.assertEqual(instance.first_element, int(first_id))
        self.assertEqual(instance.last_element, int(last_id))
        self.assertEqual(instance.name, 'range-{0}-{1}'.format(first_id, last_id))
        with self.assertRaises(Exception):
            VlanRange((30, 10))

    def test_intersect(self):
        first_id = '20'
        last_id = '50'
        instance = VlanRange((first_id, last_id))
        self.assertTrue(instance.intersect(VlanRange((10, 20))))
        self.assertTrue(instance.intersect(VlanRange((20, 50))))
        self.assertTrue(instance.intersect(VlanRange((50, 60))))
        self.assertTrue(instance.intersect(VlanRange((30, 40))))
        self.assertFalse(instance.intersect(VlanRange((5, 19))))
        self.assertFalse(instance.intersect(VlanRange((51, 60))))

    def test_cutoff(self):
        first_id = '50'
        last_id = '250'
        instance = VlanRange((first_id, last_id))
        self.assertEqual(instance.cutoff(VlanRange((20, 100))), [VlanRange((101, 250))])
        self.assertEqual(instance.cutoff(VlanRange((200, 300))), [VlanRange((50, 199))])
        self.assertEqual(instance.cutoff(VlanRange((50, 250))), [])
        self.assertEqual(instance.cutoff(VlanRange((70, 200))), [VlanRange((50, 69)), VlanRange((201, 250))])
        self.assertEqual(instance.cutoff(VlanRange((300, 400))), [VlanRange((50, 250))])

    def test_range_from_string(self):
        self.assertEqual(VlanRange(VlanRange.range_from_string('10-20')), VlanRange((10, 20)))
        self.assertEqual(VlanRange(VlanRange.range_from_string('30')), VlanRange((30, 30)))

    def test_to_string(self):
        self.assertEqual(VlanRange((30, 40)).to_string(), '30-40')


class TestVlanRangeOperations(TestCase):
    def setUp(self):
        pass

    def test_create_from_dict(self):
        vlan_dict = {'test1': '10-20', 'test2': '40-50'}
        range_list = VlanRangeOperations.create_from_dict(vlan_dict)
        self.assertEqual(range_list, [VlanRange((10, 20)), VlanRange((40, 50))])

    def test_cutoff_intersection(self):
        test_range = VlanRange((100, 500))
        result = VlanRangeOperations.cutoff_intersection([test_range], [VlanRange((150, 200)), VlanRange((300, 350))])
        self.assertEqual(result, [VlanRange((100, 149)), VlanRange((201, 299)), VlanRange((351, 500))])

    def test_find_intersection(self):
        test_range = VlanRange((200, 300))
        range_list = [VlanRange((50, 100)), VlanRange((150, 200)), VlanRange((250, 270)), VlanRange((301, 400))]
        self.assertEqual(VlanRangeOperations.find_intersection([test_range], range_list),
                         [VlanRange((150, 200)), VlanRange((250, 270))])
