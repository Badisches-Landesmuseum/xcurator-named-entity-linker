class RabbitMQ:

    def __init__(self, rabbit_config: dict):
        self.amqp_url = f"amqp://{rabbit_config['username']}:{rabbit_config['password']}@" \
                        f"{rabbit_config['host']}:{rabbit_config['port']}{rabbit_config['vhost']}"

    def connection_string(self):
        return self.amqp_url
