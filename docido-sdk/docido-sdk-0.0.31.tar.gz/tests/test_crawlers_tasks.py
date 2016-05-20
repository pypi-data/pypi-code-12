import unittest

from docido_sdk.crawler.tasks import (
    check_custom_concurrency,
    reorg_crawl_tasks,
    split_crawl_tasks,
)


class TestCrawlersTasks(unittest.TestCase):
    def test_check_custom_concurrency(self):
        ccc = check_custom_concurrency
        self.assertEqual(ccc(0, 2), 0)
        self.assertEqual(ccc(1, 1), 1)
        self.assertEqual(ccc(4, 3), 3)
        self.assertEqual(ccc(1, "bla"), 1)
        self.assertEqual(ccc(2, 0), 2)

    def test_reorg_crawl_tasks(self):
        rct = reorg_crawl_tasks
        self.assertEqual(
            rct(dict(tasks=[1, 2, 3], epilogue='e'), 1),
            ([1, 2, 3], 'e', 1)
        )
        self.assertEqual(
            rct(dict(tasks=[1, 2, 3], max_concurrent_tasks=42), 2),
            ([1, 2, 3], None, 2)
        )

    def test_split_crawl_tasks(self):
        sct = split_crawl_tasks
        self.assertEqual(sct([1, 2, 3], 2), [[1, 2], [3]])
        self.assertEqual(sct([1, 2, 3], 1), [[1, 2, 3]])
        self.assertEqual(sct([[1, 2, 3], [3]], 2), [[1, 2, 3], [3]])
        with self.assertRaises(Exception) as exc:
            self.assertEqual(sct([[1, 2], 42], 1))
        self.assertEqual(exc.exception.message, 'Expected a list of tasks')


if __name__ == '__main__':
    unittest.main()
