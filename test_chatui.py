from unittest import TestCase
from chatui import format_output


class ChatUITests(TestCase):

    def test_format_output_empty(self):
        self.assertEqual(format_output(15, "*", ""), "*             ")

    def test_format_output_one_word(self):
        self.assertEqual(format_output(15, "*", "hello"), "* hello       ")

    def test_format_output_words_to_end_of_line(self):
        self.assertEqual(format_output(15, "*", "hello, world"), "* hello, world")

    def test_format_output_word_wrap(self):
        self.assertEqual(format_output(15, "*", "hello, world!"), "* hello,      \r\n  world!      ")

    def test_format_output_with_username(self):
        self.assertEqual(format_output(15, "user *", "hello, world!"), "user * hello, \r\n  world!      ")

    def test_format_output_break_long_word(self):
        self.assertEqual(format_output(15, "*", "hello, (thiswillbebrokenacrossmultiplelines) world!"),
                         "* hello,      \r\n  (thiswillbeb\r\n  rokenacrossm\r\n  ultiplelines\r\n  ) world!    ")
