def setup_stream_listener(self):
    """
    Setup Twitter API streaming listener
    """
    listener = Listener()
    listener.set_callback(self.mq.producer.publish)
    self.stream = tweepy.Stream(
        self.config.get('twitter', 'userid'),
        self.config.get('twitter', 'password'),
        listener,
        timeout=3600
    )