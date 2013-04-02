import bs4
import urllib2
import unittest


class Comment(object):
    def addDate(self, date):
        self.date = date.encode('utf-8')
        return self

    def addAuthorUrl(self, author_url):
        self.authorUrl = author_url
        return self

    def addAuthor(self, author):
        self.author = author.encode('utf-8')
        return self

    def addText(self, text):
        self.text = text.encode('utf-8')
        return self

    def __init__(self, date, author_url, author, text):
        self.addDate(date).addAuthorUrl(author_url).addAuthor(author).addText(text)


class Scraper(object):
    def __init__(self, url):
        self.url = url
        self.html = urllib2.urlopen(url)
        self.soup = bs4.BeautifulSoup(self.html)

    def extract_comments(self):
        comments_list = self.soup.find_all(class_="commentlist")[0]
        comments_list = comments_list.find_all(class_="comment")
        comments = []
        for comment in comments_list:
            if isinstance(comment, basestring):
                continue
            parsed_comment = self.extract_comment(comment)
            comments.append(parsed_comment)
        return comments

    def extract_comment(self, comment):
        raise NotImplementedError

class GowersScraper(Scraper):
    def extract_comment(self, comment):
        try:
            date = comment.small.a.string
            text = "".join(filter(lambda x : x is not None, [x.string for x in comment.find_all("p")]))
            author_url = comment.cite.a['href']
            author = comment.cite.a.string
        except Exception as e:
            author_url = None
            author = comment.cite.string
        return Comment(date=date, text=text, author_url=author_url, author=author)

class TaoScraper(Scraper):
    def extract_comment(self, comment):
        comment_metadata = comment.find_all(class_="comment-metadata")[0]
        comment_permalink = comment_metadata.find_all(class_="comment-permalink")[0]
        date = comment_permalink.a.string
        comment_author = comment_metadata.find_all(class_="comment-author")[0]
        try:
            author = comment_author.a.string
            author_url = comment_author.a['href']
        except:
            author = comment_author.strong.string
            author_url = None
        comment_content = comment.find_all(class_="comment-content")[0]
        text = "".join(filter(lambda x: x is not None, [x.string for x in comment_content.find_all("p")]))
        return Comment(date=date, text=text, author_url=author_url, author=author)

class MultipleScraper(object):
    def __init__(self, urls):
        self.scrapers = []
        for url in urls:
            if 'terrytao.wordpress.com' in url:
                self.scrapers.append(TaoScraper(url))
            elif 'gowers.wordpress.com' in url:
                self.scrapers.append(GowersScraper(url))

    def extract_comments(self):
        all_comments = [scraper.extract_comments() for scraper in self.scrapers]
        # flatten
        return [comment for comments in all_comments for comment in comments]

class ScraperTest(unittest.TestCase):
    def testScraperGowers(self):
        s = GowersScraper("http://gowers.wordpress.com/2009/01/27/is-massively-collaborative-mathematics-possible/")
        comments_list = s.extract_comments()
        import csv
        writer=csv.DictWriter(open('test.csv', 'w'), fieldnames=['date', 'authorUrl', 'author', 'text'])
        for comment in comments_list:
            print comment.__dict__
            writer.writerow(comment.__dict__)

    def testScraperTao(self):
        s = TaoScraper("http://terrytao.wordpress.com/2009/02/05/upper-and-lower-bounds-for-the-density-hales-jewett-problem/")
        comments_list = s.extract_comments()
        import csv
        writer=csv.DictWriter(open('test.csv', 'w'), fieldnames=['date', 'authorUrl', 'author', 'text'])
        for comment in comments_list:
            print comment.__dict__
            writer.writerow(comment.__dict__)

    def testMultipleScraper(self):
        urls = [
            "http://gowers.wordpress.com/2009/02/01/a-combinatorial-approach-to-density-hales-jewett/",
            "http://terrytao.wordpress.com/2009/02/05/upper-and-lower-bounds-for-the-density-hales-jewett-problem/",
            "http://gowers.wordpress.com/2009/02/06/dhj-the-triangle-removal-approach/"
            "http://gowers.wordpress.com/2009/02/08/dhj-quasirandomness-and-obstructions-to-uniformity",
            "http://gowers.wordpress.com/2009/02/13/dhj-possible-proof-strategies/#more-441/",
            "http://terrytao.wordpress.com/2009/02/11/a-reading-seminar-on-density-hales-jewett/",
            "http://terrytao.wordpress.com/2009/02/13/bounds-for-the-first-few-density-hales-jewett-numbers-and-related-quantities/",
            "http://gowers.wordpress.com/2009/02/23/brief-review-of-polymath1/",
            "http://gowers.wordpress.com/2009/03/02/dhj3-851-899/",
            "http://terrytao.wordpress.com/2009/03/04/dhj3-900-999-density-hales-jewett-type-numbers/",
            "http://gowers.wordpress.com/2009/03/10/problem-solved-probably/"
        ]
        mscraper = MultipleScraper(urls)
        print mscraper.extract_comments()
        comments_list = mscraper.extract_comments()
        import csv
        writer=csv.DictWriter(open('all.csv', 'w'), fieldnames=['date', 'authorUrl', 'author', 'text'])
        for comment in comments_list:
            print comment.__dict__
            writer.writerow(comment.__dict__)





