from script.extra.instagram.browser.InstagramMiddleware import InstagramMiddleware
from script.extra.events.browser_events.BrowserBaseEvent import BrowserBaseEvent
from script.models.Thread import Thread
from script.models.Message import Message


class BrowserGetThreadMessagesEvent(InstagramMiddleware):
    base = None
    thread = None
    db_message = None
    text = None

    def execute(self):
        self.ig.account.add_cli('Getting unread messages ...')

        self.base = BrowserBaseEvent(self.ig)
        self.base.go_to_threads()
        self.init()

    def init(self):
        self.scroll_and_process_unread_conversations(30)

    def scroll_and_process_unread_conversations(self, scroll_times):
        self.ig.account.add_cli(f'Starting to scroll and process unread conversations over {scroll_times} scrolls')

        for _ in range(scroll_times):
            self.get_and_process_unread_conversations()
            self.scroll(1)  # Scroll a single time

    def scroll(self, times):
        for _ in range(times):
            self.ig.page.evaluate('''
                   (selector) => {
                       const element = document.querySelector(selector);
                       if (element) {
                           element.scrollTop = element.scrollTop + 400;
                       }
                   }
               ''', '.x78zum5.xdt5ytf.x1iyjqo2.xs83m0k.x1xzczws.x6ikm8r.x1rife3k.x1n2onr6.xh8yej3.x16o0dkt')

            self.ig.pause(2000, 3000)

    def get_and_process_unread_conversations(self):
        elem_selector = 'div[role="listitem"]:has(span.x6s0dn4.xzolkzo.x12go9s9.x1rnf11y.xprq8jg.x9f619.x3nfvp2.xl56j7k.x1tu34mt.xdk7pt.x1xc55vz.x1emribx)'
        unread_conversations = self.ig.page.locator(elem_selector).all()

        counter = 0

        for conversation in unread_conversations:
            counter += 1
            self.ig.account.add_cli(f'Processing {counter} unread conversation')

            self.click_on_conversation(conversation)
            self.ig.pause(3000, 3800)
            self.thread = Thread.select().where(Thread.thread_url_id == self.base.get_thread_id()).first()

            if not self.thread:
                self.ig.account.add_cli(f'Thread with url_id {self.base.get_thread_id()} does not exist')
                continue

            self.extract_messages()

    def extract_messages(self):
        parent_elements_selector = 'div.html-div.xexx8yu.x4uap5.x18d9i69.xkhd6sd.x1gslohp.x11i5rnm.x12nagc.x1mh8g0r.x1yc453h.x126k92a.x18lvrbx'

        parent_elements = self.ig.page.locator(parent_elements_selector).all()

        for message_parent in parent_elements:
            self.text = message_parent.inner_html()

            self.db_message = Message.select().where(
                (Message.thread == self.thread) &
                (Message.text.contains(self.text))
            ).first()

            if not self.db_message:
                self.ig.account.add_cli(f'We have new message with the txt of : {self.text}')

                self.new_message_process()

    def new_message_process(self):
        state_mapper = {
            'dm follow up': 'unseen dm reply',
            'unseen dm reply': 'unseen dm reply',
            'seen dm reply': 'unseen dm reply',

            'interested': 'interested',
            'not interested': 'not interested',
            'needs response': 'needs response',

            'loom follow up': 'unseen loom reply',
            'unseen loom reply': 'unseen loom reply',
            'seen loom reply': 'unseen loom reply',
            'free': 'free'
        }

        self.thread.lead.change_state(
            account=self.ig.account,
            state=state_mapper[self.thread.lead.last_state],
            update_date=True
        )

        self.db_message = Message.create(
            thread=self.thread,
            text=self.text,
            sender='lead',
            type='text',
            state='unseen',
        )

    def click_on_conversation(self, conversation):
        try:
            conversation.click()
            self.ig.account.add_cli('Conversation clicked')

        except Exception as e:
            self.ig.account.add_cli(f'Problem clicking on unread conversation : {e}')
