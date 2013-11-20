import sys
import subprocess
import json
import settings
import hipchat


class Lottery(object):
    """
    Lottery class use curl command in shell.
    """
    login_req = "curl -X POST " \
                "--user-agent 'Mozilla/5.0 (iPhone; CPU iPhone OS 5_1 like Mac OS X) " \
                "AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 Mobile/9B179 Safari/7534.48.3' " \
                "http://event.ozwiz.actoz.com/WebSvc/MaEventWebSvc.asmx/WebLogIn " \
                "-H 'Content-Type: application/json; charset=utf-8' " \
                "--data '{\"a_sMaID\": \"%s\", \"a_sMaCode\": \"%s\"}' " \
                "-H 'Content-Length: 44'"
    draw_req = "curl -X POST --user-agent 'Mozilla/5.0 (iPhone; CPU iPhone OS 5_1 like Mac OS X)" \
                  " AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 Mobile/9B179 Safari/7534.48.3' " \
                  "http://event.ozwiz.actoz.com//WebSvc/MaEventWebSvc.asmx/WebGacha " \
                  "-H 'Content-Type: application/json; charset=utf-8' " \
                  "--data '{\"a_sMaID\": \"%s\", \"a_sMaCode\": \"%s\"}' " \
                  "-H 'Content-Length: 44'"

    def get_lottery(self, id, visit_code):
        """
        Try to login and get a lottery count.
        If I have enough lottery, rolling it.

        Result of login request.
        {
            u'c': u'E0qFDe2ZxbI=',
            u'cp_img': u'',
            u'cp_no': u'',
            u'issue_state': u'0',
            u'lot_cp_cnt': u'1',
            u'ret_code': u'0',
            u'u': u'xJ2luTfk2Nk='
        }
        """
        login_cmd = self.login_req % (id, visit_code)

        p = subprocess.Popen(login_cmd, shell=True,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)

        out_data, err_data = p.communicate()

        # Extract real result data from JSON string.
        result = out_data[6:-2].decode('string-escape')
        out_obj = json.loads(result)

        if out_obj['lot_cp_cnt'] == "0":
            print "Don't have any lottery ticket. Exiting."

            return False

        return self.draw_lottery(id, visit_code)

    def draw_lottery(self, id, visit_code):
        """
        If I have a lottery ticket, draw it.

        Result is
        {
            "d": "{\r\n\t\"cp_no\": \"6653085528894197HSNP\",\r\n
            \t\"cp_img\": \"popup_NM\",\r\n\t\"lot_cp_cnt\": \"0\",\r\n
            \t\"ret_code\": \"0\",\r\n\t\"cp_type\": \"4\"\r\n}"
        }
        """
        draw_cmd = self.draw_req % (id, visit_code)

        p = subprocess.Popen(draw_cmd, shell=True,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)

        out_data, err_data = p.communicate()

        # Extract real result data from JSON string.
        result = out_data[6:-2].decode('string-escape')
        out_obj = json.loads(result)

        if out_obj['cp_no'] == "":
            print "Nothing."

            return False

        return out_obj['cp_no']


if __name__ == '__main__':
    lottery = Lottery()

    if settings.MILLION_ARTHUR_ID == "":
        print "Please fill in id/visit code in settings.py."
        sys.exit(1)

    result = lottery.get_lottery(settings.MILLION_ARTHUR_ID, settings.MILLION_ARTHUR_VISIT_CODE)

    if result:
        message = "Lottery got " + result
    else:
        message = "Lottery failed"

    if settings.HIPCHAT_TOKEN == "":
        print message
        sys.exit(0)

    hipster = hipchat.HipChat(token=settings.HIPCHAT_TOKEN)

    hipster.message_room(settings.HIPCHAT_ROOM_NUMBER, "Lottery", message)

    sys.exit(0)
