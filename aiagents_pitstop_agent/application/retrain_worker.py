from threading import Event, Lock, Thread
from time import sleep
from sqlalchemy.orm import sessionmaker

retrain_event = Event()
retrain_lock = Lock()


class RetrainWorker:
    def __init__(self, training_service, session_factory: sessionmaker, stop_event: Event):
        self._training = training_service
        self._session_factory = session_factory
        self._stop_event = stop_event

    def start(self):
        Thread(target=self._run, daemon=True).start()

    def stop(self):
        self._stop_event.set()
        retrain_event.set()  

    def _run(self):
        while not self._stop_event.is_set():
            retrain_event.wait()
            retrain_event.clear()

            if self._stop_event.is_set():
                break

            if retrain_lock.locked():
                sleep(0.2)
                continue

            with retrain_lock:
                db = self._session_factory()
                try:
                    self._training.train_and_activate(db)
                    db.commit()
                except Exception as e:
                    db.rollback()
                    print(f"[RetrainWorker] retrain failed: {e}")
                finally:
                    db.close()

            sleep(0.2)
