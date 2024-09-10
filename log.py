class Log:
    @staticmethod
    def write_log(time, object, description):
        file = open('log.txt', 'a')
        note = time + ' ' + str(object) + ' ' + description
        file.write(note)
        file.write('\n')
        file.close()
