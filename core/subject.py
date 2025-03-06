from kivy.event import EventDispatcher

class Subject(EventDispatcher):
    """
    Base class for implementing the Observer Pattern in Kivy.
    Classes that inherit from Subject can dispatch 'on_data_updated'
    whenever their data changes.
    """
    __events__ = ("on_data_updated",)

    def notify(self,event, data):
        """
        Dispatches an event, sending 'data' to any bound observers.
        Example usage in child classes:
            self.notify(new_value)
        """
        self.dispatch("on_data_updated", data)

    def on_data_updated(self, data):
        """
        This event is automatically recognized because it's in __events__.
        Observers can bind to 'on_data_updated' to receive real-time updates.
        """
        pass