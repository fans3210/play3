def notify_client(skt, progress, details, room, status='complete'):
    '''
    status: processing, complete, error
    '''
    skt.emit('data_status', {
        "progress": progress,
        "details": details,
        "status": status
    }, namespace='/datasocket', room=room)
