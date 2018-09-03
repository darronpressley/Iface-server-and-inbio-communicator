
def buildConnectionString(params):
    """Build a connection string from a dictionary of parameters.

    Returns string."""
    return ";".join(["%s=%s" % (k, v) for k, v in params.items()])

    myParams = {"server":"YEAH", \
                "database":"timeware_main_6", \
                "uid":"sa", \
                "pwd":"Sky6fall!ng" \
                }

