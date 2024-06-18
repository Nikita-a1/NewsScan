import datetime


class Log:
    @staticmethod
    def write_log(time, url, description):
        file = open('log.txt', 'a')
        note = time + ' ' + url + ' ' + description
        file.write(note)
        file.write('\n')
        file.close()


Log.write_log(str(datetime.datetime.now().today().replace(microsecond=0)), "https123", "Can't open the file")
