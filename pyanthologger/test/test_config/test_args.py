class ArgsTestCase(ConfigTestCase):
  def setUp(self):
    pass

  def test_defaults(self):
    self.assertEqual(vars(args.parse()), vars(defaults))