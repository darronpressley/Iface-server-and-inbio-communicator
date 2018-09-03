NAME = 'ifaceserver' # what the name of the service is, used in command line things like "sc"
DISPLAY_NAME = 'Ifaceserver Push Server' # display name of the service, this is what you see in the "Services" window
MODULE_NAME = 'ifaceserver.py' # python file containing the actual service code
CLASS_NAME = 'Handler' # class name of the service, since it doesn't extend anything, all it needs are certain methods
DESCRIPTION = 'push server for iface devices' # description of the service, seen in the Service Properties window
AUTO_START = False # does the service auto start?

# does the service respond to session changes? Setting this to True and implemnting SessionChanged(sessionId, eventType)
# is the only way to respond to things like Shutdown. See
# https://msdn.microsoft.com/en-us/library/windows/desktop/ms683241%28v=vs.85%29.aspx for the event types
SESSION_CHANGES = False