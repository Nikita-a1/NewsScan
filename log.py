class Log:
    @staticmethod
    def write_log(time, url, description):
        file = open('log.txt', 'a')
        note = time + ' ' + url + ' ' + description
        file.write(note)
        file.write('\n')
        file.close()
