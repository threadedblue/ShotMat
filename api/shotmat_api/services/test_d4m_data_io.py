import unittest
import D4M.assoc as d4m_assoc
from shotmat.api.shotmat_api.persistence.d4m_data_io import writejson, readjson


class TestD4MDataIO(unittest.TestCase):

    def test_roundtrip_serialization(self):
        """
        Tests that serializing an Assoc to JSON and back results in an
        equivalent Assoc.
        """
        # 1. Create a sample Assoc
        original_assoc = d4m_assoc.Assoc("", "", "")
        original_assoc.set("row1", "colA", "value1A")
        original_assoc.set("row1", "colC", "123")
        original_assoc.set("row2", "colB", "value2B")
        original_assoc.set("row3", "colA", "value3A")

        # 2. Serialize to JSON
        json_data = writejson(original_assoc)

        # 3. Check the JSON structure
        self.assertIn("rows", json_data)
        self.assertIn("cols", json_data)
        self.assertIn("entries", json_data)

        self.assertEqual(sorted(json_data["rows"]), ["row1", "row2", "row3"])
        self.assertEqual(sorted(json_data["cols"]), ["colA", "colB", "colC"])
        self.assertEqual(len(json_data["entries"]), 4)

        # Check one entry to be sure
        self.assertIn({"row": "row1", "col": "colA", "val": "value1A"}, json_data["entries"])

        # 4. Deserialize back to an Assoc
        reconstructed_assoc = readjson(json_data)

        # 5. Verify equivalence
        self.assertEqual(original_assoc.num_entries(), reconstructed_assoc.num_entries())
        
        # Check that all original values are present in the new assoc
        r, c, v = original_assoc.find()
        for i in range(len(r)):
            self.assertEqual(reconstructed_assoc.get(r[i], c[i]), v[i])

    def test_readjson_missing_keys(self):
        """
        Tests that readjson raises ValueError for malformed input.
        """
        with self.assertRaisesRegex(ValueError, "must contain 'rows', 'cols', and 'entries'"):
            readjson({"rows": [], "cols": []}) # Missing 'entries'

        with self.assertRaisesRegex(ValueError, "must contain 'rows', 'cols', and 'entries'"):
            readjson({"rows": [], "entries": []}) # Missing 'cols'

        with self.assertRaisesRegex(ValueError, "must contain 'rows', 'cols', and 'entries'"):
            readjson({"cols": [], "entries": []}) # Missing 'rows'

    def test_readjson_malformed_entry(self):
        """
        Tests that readjson raises ValueError for a malformed entry.
        """
        bad_data = {
            "rows": ["r1"],
            "cols": ["c1"],
            "entries": [{"row": "r1", "value": "v1"}] # 'value' instead of 'val'
        }
        with self.assertRaisesRegex(ValueError, "Malformed entry"):
            readjson(bad_data)

if __name__ == '__main__':
    unittest.main()