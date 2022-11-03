class TakePicturesHandler:
    x = 0
    y = 0
    z = 0
    w_icrement = 340
    h_increment = 230
    garden_w = 2500
    garden_h = 1230
    beginning = True
    mqtt_client = None
    photo_request_id = None
    reverse_movement = False
    y_changed = False

    # The `on_connect` event is called whenever the device
    # connects to the MQTT server. You can place initialization
    # logic here.
    #
    # The callback is passed a FarmBot instance, plus an MQTT
    # client object (see Paho MQTT docs to learn more).
    def on_connect(self, bot, mqtt_client):
        self.mqtt_client = mqtt_client
        # Once the bot is connected, we can send RPC commands.
        # Every RPC command returns a unique, random request
        # ID. Later on, we can use this ID to track our commands
        # as they succeed/fail (via `on_response` / `on_error`
        # callbacks):
        print(" initial position " + str(bot.position()))
        request_id1 = bot.move_absolute(x=self.x, y=self.y, z=self.z)
        print("MOVE_ABS REQUEST ID: " + request_id1)

    def on_change(self, bot, state):
        # The `on_change` event is most frequently triggered
        # event. It is called any time the device's internal
        # state changes. Example: Updating X/Y/Z position as
        # the device moves across the garden.
        # The bot maintains all this state in a single JSON
        # object that is broadcast over MQTT constantly.
        # It is a very large object, so we are printing it
        # only as an example.
        print("NEW BOT STATE TREE AVAILABLE:")
        # print(state)
        # Since the state tree is very large, we offer
        # convenience helpers such as `bot.position()`,
        # which returns an (x, y, z) tuple of the device's
        # last known position:
        print("Current position: (%.2f, %.2f, %.2f)" % bot.position())
        # A less convenient method would be to access the state
        # tree directly:
        # pos = state["location_data"]["position"]
        # xyz = (pos["x"], pos["y"], pos["z"])
        # print("Same information as before: " + str(xyz))
        positins = bot.position()
        if int(self.x) + 2 >= int(positins[0]) >= int(self.x) - 2  \
                and int(self.y) + 2 >= int(positins[1]) >= int(self.y) - 2 \
                and int(positins[2]) == int(self.z)\
                and not state['informational_settings']['busy']\
                and self.photo_request_id is None:
            print("Taking photo in " + str(bot.position()))
            # start take photo request
            self.photo_request_id = bot.take_photo()


    # The `on_log` event fires every time a new log is created.
    # The callback receives a FarmBot instance, plus a JSON
    # log object. The most useful piece of information is the
    # `message` attribute, though other attributes do exist.
    def on_log(self, bot, log):
        print("New message from FarmBot: " + log['message'])

    # When a response succeeds, the `on_response` callback
    # fires. This callback is passed a FarmBot object, as well
    # as a `response` object. The most important part of the
    # `response` is `response.id`. This `id` will match the
    # original request ID, which is useful for cross-checking
    # pending operations.
    def on_response(self, bot, response):
        print("ID of successful request: " + response.id)
        if response.id == self.photo_request_id:
            self.photo_request_id = None
            if (self.x < self.garden_w - 1 or self.y < self.garden_h - 1) and self.x > -1:
                if self.y_changed:
                    self.y_changed = False
                elif self.x >= self.garden_w - 1:
                    self.y_changed = True
                    if self.beginning:
                        self.beginning = False
                    self.reverse_movement = True
                    self.increase_y(bot.position()[1])
                elif 10 >= self.x >= - self.w_icrement and not self.beginning:
                    self.y_changed = True
                    self.reverse_movement = False
                    self.increase_y(bot.position()[1])
                if not self.y_changed:
                    if self.reverse_movement:
                        self.decrease_x(bot.position()[0])
                    else:
                        self.increase_x(bot.position()[0])
                bot.move_absolute(x=self.x, y=self.y, z=self.z)
            else:
                print("Disconnecting")
                self.mqtt_client.disconnect()
    # If an RPC request fails (example: stalled motors, firmware
    # timeout, etc..), the `on_error` callback is called.
    # The callback receives a FarmBot object, plus an
    # ErrorResponse object.

    def on_error(self, bot, response):
        # Remember the unique ID that was returned when we
        # called `move_absolute()` earlier? We can cross-check
        # the ID by calling `response.id`:
        print("ID of failed request: " + response.id)
        # We can also retrieve a list of error message(s) by
        # calling response.errors:
        print("Reason(s) for failure: " + str(response.errors))

    def increase_y(self, position_y):
        if position_y + self.h_increment >= self.garden_h - 1:
            self.y = self.garden_h - 1
        else:
            self.y = position_y + self.h_increment

    def increase_x(self, position_x):
        if position_x + self.w_icrement >= self.garden_w - 1:
            self.x = self.garden_w - 1
        else:
            self.x = position_x + self.w_icrement

    def decrease_x(self, position_x):
        if position_x - self.w_icrement < 0:
            self.x = 0
        else:
            self.x = position_x - self.w_icrement



