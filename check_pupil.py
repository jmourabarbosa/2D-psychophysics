import zmq
from multiprocessing import Process, Value,Array
from time import sleep

#Pupil network setup
port = "5000"
localhost="tcp://127.0.0.1:"

def test_pupil():

    def test_pupil_aux():

        context = zmq.Context()
        socket = context.socket(zmq.SUB)
        socket.connect(localhost+port)
        socket.setsockopt(zmq.SUBSCRIBE, '')

        msg = socket.recv()
        print "msg",msg

    p=Process(target=test_pupil_aux)
    p.start()
    sleep(1)


    if p.is_alive():
        p.terminate()
        return False

    return True

if __name__ == "__main__":
    if test_pupil():
        print "Pupil is working!"
    else:
        print "Pupil is not responding."