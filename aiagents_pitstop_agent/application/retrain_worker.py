from threading import Event, Lock, Thread
from sqlalchemy.orm import sessionmaker
from time import sleep

retrain_event = Event()
stop_event = Event()
retrain_lock = Lock()


class RetrainWorker:
    def __init__(self, training_service, session_factory: sessionmaker):
        self._training = training_service
        self._session_factory = session_factory

    def start(self):
        Thread(target=self._run, daemon=True).start()

    def stop(self):
        stop_event.set()
        retrain_event.set()

    def _run(self):
        while not stop_event.is_set():
            retrain_event.wait()
            retrain_event.clear()

            if stop_event.is_set():
                break

            if retrain_lock.locked():
                continue

            with retrain_lock:
                db = self._session_factory()
                try:
                    self._training.train_and_activate(db)
                    db.commit()
                except Exception:
                    db.rollback()
                finally:
                    db.close()

            sleep(0.2)
