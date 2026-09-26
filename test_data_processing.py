import unittest
import pandas as pd
from data_processing import limpiar_datos, serie_mensual


class FechasTest(unittest.TestCase):
    def clean(self, rows):
        result, error = limpiar_datos(pd.DataFrame(rows))
        self.assertIsNone(error)
        return result

    def test_missing_dates_are_not_invented(self):
        data = self.clean([{'total': 20}, {'total': 30}])
        self.assertTrue(data['month'].isna().all())
        self.assertTrue(data['contracts'].isna().all())
        self.assertEqual(data.total.sum(), 50)
        self.assertTrue(serie_mensual(data).empty)

    def test_real_dates_override_conflicting_parts(self):
        data = self.clean([{'monto': 20, 'fecha': '2024-03-10', 'mes': 8, 'anio': 2025}])
        self.assertEqual(data.iloc[0]['month'], 3)
        self.assertEqual(data.iloc[0]['anio'], 2024)

    def test_invalid_months_are_excluded(self):
        data = self.clean([{'total': 10, 'month': m, 'anio': 2025} for m in [0, 13, 2.5, 'bad', None, 12]])
        self.assertEqual(data.month.notna().sum(), 1)
        self.assertEqual(serie_mensual(data).iloc[0]['ds'], pd.Timestamp('2025-12-01'))

    def test_invalid_dates_do_not_become_1970(self):
        data = self.clean([{'total': 10, 'date': d} for d in [12345, 'bad', None]])
        self.assertTrue(data['month'].isna().all())

    def test_same_month_different_years_stay_separate(self):
        data = self.clean([{'total': 10, 'month': 1, 'anio': 2024},
                           {'total': 20, 'month': 1, 'anio': 2025},
                           {'total': 30, 'month': 1, 'anio': 2025}])
        monthly = serie_mensual(data)
        self.assertEqual(monthly.y.tolist(), [10, 50])
        self.assertEqual(len(monthly), 2)

    def test_observed_parts_without_full_date(self):
        data = self.clean([{'total': 10, 'mes': '2', 'year': '2025'}])
        self.assertEqual(serie_mensual(data).iloc[0]['ds'], pd.Timestamp('2025-02-01'))

    def test_partial_missingness_retains_non_temporal_totals(self):
        data = self.clean([{'total': 10, 'date': '2025-02-01'}, {'total': 20}])
        self.assertEqual(data.total.sum(), 30)
        self.assertEqual(serie_mensual(data).y.sum(), 10)

    def test_missing_total_fails_clearly(self):
        data, error = limpiar_datos(pd.DataFrame([{'month': 1}]))
        self.assertIsNone(data)
        self.assertIn('monto', error)

    def test_contracts_are_observed_nonnegative_integers(self):
        data = self.clean([{'total': 10, 'contracts': x} for x in [-1, 2.5, None, 0, 5]])
        self.assertEqual(data.contracts.notna().sum(), 2)
        self.assertEqual(data.contracts.sum(), 5)

    def test_source_is_not_modified(self):
        source = pd.DataFrame([{'monto': '10', 'mes': '2'}])
        original = source.copy(deep=True)
        limpiar_datos(source)
        pd.testing.assert_frame_equal(source, original)


if __name__ == '__main__':
    unittest.main()
