try:
    from app import app
    import unittest


except Exception as e:
    print("some modules are missing {}".format(e))


class Test(unittest.TestCase):
    # check if responses is 200
    def test_user_register(self):
        test = app.test_client(self)
        response = test.get('/user-registration/')
        status = response.status_code
        self.assertEqual(status, 405)

    def test_products(self):
        test = app.test_client(self)
        response = test.get('/show-appointments/')
        status = response.status_code
        self.assertEqual(status, 200)

    def test_product_id(self):
        test = app.test_client(self)
        response = test.get('/get-hotels/')
        status = response.status_code
        self.assertEqual(status, 200)


if __name__ == '__main__':
    unittest.main()
