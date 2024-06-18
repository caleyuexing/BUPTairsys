import os
from logging import StreamHandler
from celery import current_task
from celery.signals import task_prerun, task_postrun
 
 
class CeleryTaskLoggerHandler(StreamHandler):
    terminator = "\r\n"
 
    def __init__(self, *args, **kwargs):
        self.task_id_fd_mapper = {}
        super().__init__(*args, **kwargs)
        # 使用 celery的task信号，设置任务开始和结束时的执行的东西
        # 主要是获取task_id 然后创建对应的独立任务日志文件
        task_prerun.connect(self.on_task_start)
        task_postrun.connect(self.on_start_end)
 
    @staticmethod
    def get_current_task_id():
        # celery 内置提供方法获取task_id
        if not current_task:
            return
        task_id = current_task.request.root_id
        return task_id
 
    def on_task_start(self, sender, task_id, **kwargs):
        # 这里是根据task_id 定义每个任务的日志文件存放
        log_path = os.path.join('logs/celery/', f"{task_id}.log")
        f = open(log_path, 'a')
        self.task_id_fd_mapper[task_id] = f
 
    def on_start_end(self, sender, task_id, **kwargs):
        f = self.task_id_fd_mapper.pop(task_id, None)
        if f and not f.closed:
            f.close()
        self.task_id_fd_mapper.pop(task_id, None)
 
    def emit(self, record):
        # 自定义Handler必须要重写的一个方法
        task_id = self.get_current_task_id()
        if not task_id:
            return
        try:
            f = self.task_id_fd_mapper.get(task_id)
            self.write_task_log(f, record)
            self.flush()
        except Exception:
            self.handleError(record)
 
    def write_task_log(self, f, record):
        # 日志的实际写入
        if not f:
            raise ValueError('Not found thread task file')
        msg = self.format(record)
        f.write(msg)
        f.write(self.terminator)
        f.flush()
 
    def flush(self):
        for f in self.task_id_fd_mapper.values():
            f.flush()
 