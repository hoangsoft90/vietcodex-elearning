__author__ = 'Hoang'
from firebase import firebase

class Elearning:
    #vietcode class reference
    vcdx =None;
    _firebase =None

    firebase_url = "https://hoangweb.firebaseio.com"
    firebase_processor_path = "/vietcodex/elearning/processor"

    learning_path = "video.html"

    def __init__(self,parent=None):
        #super(Elearning, self).__init__()  #no inheritance
        self.vcdx= parent

        #since we move client to hosting
        #self.livestream_client_site = "http://%s:%s/%s"% (self.vcdx.localIP,self.vcdx.nginx_http_port, self.learning_path)
        self.livestream_client_site = "http://vietcodex.edu.vn/video.html"

        self._firebase = firebase.FirebaseApplication(self.firebase_url, None)
        pass

    """
    get local IP from teacher computer
    we modify c:/python27/Lib/site-package/firebase/firebase.py to adding arg veriy=False to disable SSL
    because .put method bellow has no option to change it.
    """
    def storeLocalIP(self):
        #_firebase.put('/vietcodex/elearning/localIP', "192.168.1.114");
        result = self._firebase.put(self.firebase_processor_path, 'IP',self.vcdx.localIP )
        #result = _firebase.post('/vietcodex/elearning/localIP', "192.168.1.114")
        #update client URL
        self._firebase.put(self.firebase_processor_path, 'URL', self.livestream_client_site )

        #get
        #result = _firebase.get('/vietcodex/elearning/processor','IP')
        print result

    """
    active elearning site by set /vietcodex/elearning/processor/active=1 on my db
    """
    def activeElearning_site(self,active="1"):
        result = self._firebase.put(self.firebase_processor_path, 'active',active )