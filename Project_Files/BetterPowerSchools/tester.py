q = "INSERT INTO messages (messageID, message)"
messages = Query(q)
a = []
for message in messages:
    m = BPS.Message()
    m.init(message)
    a.append(m)
for message in a:
    print(m.)
