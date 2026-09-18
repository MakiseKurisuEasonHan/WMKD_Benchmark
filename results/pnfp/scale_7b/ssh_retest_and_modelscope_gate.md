# SSH 重测与 ModelScope gate

用户更新：公钥已配置，要求优先在新 AutoDL 用 ModelScope CLI/SDK 检查 xinyuzhang/Llama-2-7b-hf，其次 f541119578/Llama-2-7b-hf。先核对 metadata/file list/config/tokenizer/非量化HF权重/大小/provenance，再小文件或单shard测速；速度合适后完整下载。暂不选择Base或Chat，先依据A2实际代码核实，不改变协议。

## 实际执行

普通沙箱 SSH 报网络 Permission denied；随后经批准在沙箱外重测，TCP和SSH握手成功，服务器认证仍失败。追加一次 `ssh -vv -o BatchMode=yes -o ConnectTimeout=15 -o StrictHostKeyChecking=yes -p 47990 root@connect.westd.seetacloud.com exit` 定位认证问题。

- endpoint：36.103.198.204:47990；remote OpenSSH_8.9p1 Ubuntu。
- known-host ED25519一致：SHA256:liZ36vNCsNcNdXeWs4f+g5ZIhPM/ZihP834vxs8Ulqc。
- 本机提供 id_ed25519，公钥指纹：SHA256:A+akuH4O+1KmneqxzY6K/23le9R+Jk4rsXzJeny7kWk。
- `Offering public key` 后服务器继续要求 publickey/password，没有接受该钥匙。
- 结果：`Permission denied (publickey,password)`；没有进入远程shell。

因此ModelScope在AutoDL上的可达性、SDK状态、仓库完整性、config/tokenizer、权重格式和大小均未验证。下载MB/s、全量ETA和实际磁盘占用均为NOT_MEASURED。网页工具也无法读取两个候选的files页面；此结果不表示AutoDL无法访问ModelScope。

## A2 代码证据

- configs/watermark/pnfp_experiment_a2.yaml 固定原始 meta-llama/Llama-3.2-3B-Instruct revision。
- scripts/pnfp_a2_speed_smoke_train.py:26 将实际 model_path 传给官方 finetune，model_size标签3B-Instruct；:32 use_chat_template=True。
- scripts/pnfp_experiment_a_pipeline.py:93起的fingerprint构造也启用chat模板；A2复用同一已冻结fingerprints。
- detector与SFT formatter同样有chat模板依赖。因此标准HF/非量化文件格式通过，尚不等于满足本轮初始化/模板科学等价要求。
- 按最新用户要求不选择Base/Chat，也不把仓库名作为模型科学身份的充分证据。

下一动作：核对新实例root authorized_keys与上述公钥、目录/文件权限或指定用户配置的另一私钥路径；认证成功后直接进行ModelScope SDK与小文件/单shard测速。没有模型下载、GPU任务、旧结果修改、清理、上传、邮件、Git提交或关机。

## 6003 alias 更新后的真实重测

用户提供 `C:\Users\Eason.ssh\config`，该路径经沙箱外检查不存在；实际文件为 `C:\Users\Eason\.ssh\config`，132 bytes。使用实际config执行`6003 -G`确认解析为root / connect.westd.seetacloud.com / 47990 / IdentityFile C:\Users\Eason\.ssh\id_ed25519。

经批准的 `ssh -F "C:\Users\Eason\.ssh\config" 6003 -o BatchMode=yes -o ConnectTimeout=15 -v "pwd; df -h /root/autodl-tmp; nvidia-smi"` 已实际执行，日志明确Applying options for 6003、Connection established、Offering public key (explicit)，但服务器仍拒绝同一SHA256:A+akuH4O+1KmneqxzY6K/23le9R+Jk4rsXzJeny7kWk公钥，退出码1。普通交互模式连接无输出等待，已通过该工具session的Ctrl-C停止；没有远程worker。

用户报告数据盘升级到70GB可用，因认证失败尚未以df独立实测。已询问用户成功登录是否通过密码或另一把钥匙；无需重复批准实验，只需修复实际认证差异。ModelScope检查、下载测速与GPU测速仍未运行。
