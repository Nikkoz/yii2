from .main import Main

class CBloomberg(Main):
    def __init__(self, link, posts, handbook):
        Main.__init__(self, link, posts, handbook)

        self.result = []

    def start(self):
        try:
            self.get_news(self.check_url('/technology'))
        except RuntimeError as error:
            self.log.write("Error: {0}".format(error))

        self.log.write("End: added {0} posts".format(len(self.result)))

    def get_news(self, url):
        self.set_file(url)

        soup = self.soup()

        wrapper = soup.find('section', {'class': 'hub-zone-righty__content'})

        try:
            blocks = wrapper.find_all('article')
        except AttributeError:
            raise RuntimeError("structure of the news list has changed")

        for block in blocks:
            h3 = block.find('h3')

            if h3 is None:
                a = block.find('a', {'class': 'single-story-module__headline-link'})
            else:
                try:
                    a = h3.find('a')
                except AttributeError:
                    raise RuntimeError("structure of the news list has changed")

            url = self.check_url(a.get('href'))
            title = a.text.strip()

            if title in self.posts:
                continue

            try:
                post = self.get_post(url)

                if post:
                    if self.check_date(post['date']) is None:
                        break

                    handbook = self.check_handbook_post(title, post['content'])

                    if handbook:
                        self.result.append({
                            'url': url,
                            'title': title,
                            'date': post['date'],
                            'section': 'News',
                            'text': post['content'],
                            'handbook': handbook
                        })

                        self.posts.append(title)

            except Warning as error:
                self.log.write("Error: {0}".format(error))

    def get_post(self, url):
        if url is None:
            return

        self.set_file(url)

        soup = self.soup()

        content = soup.find('div', {'class': 'body-copy-v2'})
        date = soup.find('time', {'class': 'article-timestamp'})

        if content is None or date is None:
            raise Warning("structure of the news post has changed. Post link: {0}".format(url))

        text = []
        for div in content.find_all('div'):
            if not div is None:
                div.extract()

        for p in content.find_all('p'):
            script = p.script

            if not script is None:
                script.extract()

            text.append(self.clear(p.text))

        return {
            'content': '<br>'.join(text),
            'date': date.get('datetime')
        }