#coding:utf-8
#开始上传状态
STATUS_START_UPLOAD = 0
#正在上传状态
STATUS_UPLOADING = 1
#上传停止状态
STATUS_UPLOAD_STOP = 2
#上传完成状态,上传完成只是表示上传文件内容完成，并不表示该文件上传成功
STATUS_UPLOAD_FINISHED = 3
#上传成功状态,上传成功是在上传文件内容完成后，对文件hash校验通过后的状态
STATUS_UPLOAD_SUCCESS = 4
#上传失败状态
STATUS_UPLOAD_FAIL = -1


#开始下载状态
STATUS_START_DOWNLOAD = 0
#正在下载状态
STATUS_DOWNLOADING = 1
#下载停止状态
STATUS_DOWNLOAD_STOP = 2
#下载完成状态,下载完成只是表示下载文件内容完成，并不表示该文件下载成功
STATUS_DOWNLOAD_FINISHED = 3
#下载成功状态,下载成功是在下载文件内容完成后，对文件hash校验通过后的状态
STATUS_DOWNLOAD_SUCCESS = 4
#下载失败状态
STATUS_DOWNLOAD_FAIL = -1
