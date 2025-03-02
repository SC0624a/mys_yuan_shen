# 米游社——原神
[**API参考项目**](https://github.com/UIGF-org/mihoyo-api-collect)

# 版本遗留问题：
- [x] 解决**获取角色5003**
- [ ] 创建更多的功能

# 调用示例
~~~python
from mhy_ys.py import mys_api
import time

uid = input(请输入你的uid)
data = mys_api.GET_Qr_login()
qr_code = data['qr_code']
tk = data['tk']
print(f'请使用mys扫码，路径：{qr_code}')

time.sleep(3)
data = mys_api.GET_Qr_login_1(ticket=tk)
login = data['login']
print(login)

time.sleep(3)
data = mys_api.Hk4eToken(uid)
print(data['play'])

time.sleep(3)
data = mys_api.yuan_shen_jue_se_data()
print(data)
~~~

# 其他
> tips：或许有大佬可以推荐几个参考项目吗awa
> 
> 尝试理解过[getDeviceFP.test.ts](https://github.com/BTMuli/TGAssistant/blob/master/test/getDeviceFP.test.ts)和[request.py#L131](https://github.com/Genshin-bots/gsuid_core/blob/2aff12e8d3b74160dbcb4f4407b7b1f22d82f718/gsuid_core/utils/api/mys/request.py#L131)这两个项目~~但并没有什么收获~~
