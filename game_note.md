## table:

USER:
- username
- role

GAME:
- start_time
- end_time
- status

## page 

index:

- 如果未登陆 -> name verify code
- 已登陆，到各自的页面下 admin or player

admin:

- 未登陆 -> index
- 已登陆且是admin，展示各自页面
- 已登陆且是player，player 页面

player:

- 未登陆 -> index
- 已登陆且是admin，展示各自页面
- 已登陆且是player，player 页面


