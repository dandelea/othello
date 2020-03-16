
import functions, sys, datetime, pytz

def init_database():
    print('[{0}: RESTORE DATABASE]'.format(datetime.datetime.now(pytz.utc).isoformat()))
    functions.init_database()

def purge_disconnected():
    print('[{0}: PURGE DISCONNECTED USERS]'.format(datetime.datetime.now(pytz.utc).isoformat()))
    functions.purge_disconnected()

def purge_gameover():
    print('[{0}: PURGE GAME OVERS]'.format(datetime.datetime.now(pytz.utc).isoformat()))
    functions.purge_gameover()

def ai_plays():
    print('[{0}: AI PLAYS]'.format(datetime.datetime.now(pytz.utc).isoformat()))
    functions.ai_plays()

def ping():
    print('[{0}: PING]'.format(datetime.datetime.now(pytz.utc).isoformat()))
    functions.ping()

if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == 'ping':
            ping()
        elif sys.argv[1] == 'reset':
            init_database()
            ping()
        elif sys.argv[1] == 'purge':
            ping()
            purge_disconnected()
            purge_gameover()
        elif sys.argv[1] == 'ai':
            ping()
            ai_plays()
    else:
        ping()
        purge_disconnected()
        purge_gameover()
        ai_plays()
