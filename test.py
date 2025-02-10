'''
<template>
  <div class="auth-form">
    <div class="tab-switch">
      <router-link to="/login" class="tab-item active">登录</router-link>
      <router-link to="/register" class="tab-item">注册</router-link>
    </div>

    <el-form :model="form" :rules="currentRules" class="login-form" ref="formRef">
      <!-- 动态登录方式 -->
      <template v-if="!isSMSLogin">
        <!-- 手机号输入 -->
        <el-form-item prop="account">
          <el-input v-model="form.account" placeholder="请输入手机号或邮箱" class="phone-input">
          </el-input>
        </el-form-item>

        <!-- 密码输入 -->
        <el-form-item prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="请输入密码"
            show-password
            @keyup.enter="handleLogin"
          />
        </el-form-item>
      </template>

      <template v-else>
        <!-- 短信验证码输入 -->
        <SMSVerification verify-type="login" />
      </template>

      <!-- 登录按钮 -->
      <div class="login-buttons">
        <el-button type="primary" class="login-btn" @click="handleLogin" :loading="isLoading">
          {{ isLoading ? '登录中...' : '登录' }}
        </el-button>
        <el-button class="wechat-btn" @click="loginWithWechat">
          <el-icon><i class="iconfont icon-wechat" /></el-icon>
          微信登录
        </el-button>
      </div>

      <!-- 其他登录方式 -->
      <div class="other-options">
        <a class="login-link1" @click="toggleLoginMethod">
          {{ isSMSLogin ? '密码登录' : '短信登录' }}
        </a>
        <router-link to="/login/email-login" class="login-link2">邮箱登录</router-link>
        <router-link to="/login/forgot" class="forgot-password">忘记密码？</router-link>
      </div>
    </el-form>
  </div>
</template>

<script setup lang="ts" name="LoginIndex">
import { ref, computed } from 'vue'
import SMSVerification from '@/components/common/SMSVerification.vue'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
const userStore = useUserStore()

const isSMSLogin = ref(false)
const form = ref({
  account: '',
  phone: '',
  password: '',
  captcha: '',
})

// 添加加载状态
const isLoading = ref(false)

// 动态验证规则
const currentRules = computed(() => {
  return isSMSLogin.value ? smsRules : passwordRules
})

const passwordRules = {
  account: [
    { required: true, message: '请输入手机号或邮箱', trigger: 'blur' },
    {
      validator: (rule: any, value: string, callback: Function) => {
        if (!/^(1[3-9]\d{9}|[\w-]+@[\w-]+\.\w+)$/.test(value)) {
          callback(new Error('请输入有效的手机号或邮箱'))
        } else {
          callback()
        }
      },
      trigger: 'blur',
    },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度6-20位', trigger: 'blur' },
  ],
}

const smsRules = {
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '手机号格式不正确', trigger: 'blur' },
  ],
  captcha: [
    { required: true, message: '请输入验证码', trigger: 'blur' },
    { len: 6, message: '验证码为6位数字', trigger: 'blur' },
  ],
}

const toggleLoginMethod = () => {
  isSMSLogin.value = !isSMSLogin.value
  // 清空非当前登录方式的字段
  if (isSMSLogin.value) {
    form.value.password = ''
  } else {
    // form.value.captcha = ''
  }
}

const formRef = ref(null)

const handleLogin = async () => {
  formRef.value?.validate(async (valid: boolean) => {
    if (!valid) return

    try {
      isLoading.value = true
      const success = await userStore.loginbypassword({
        account: form.value.account,
        password: form.value.password,
      })
      if (success) {
        ElMessage.success('登录成功')
      }
    } catch (err: any) {
      ElMessage.error(err.message || '登录失败')
    } finally {
      isLoading.value = false
    }
  })
}

// 修改微信登录函数（示例）
const loginWithWechat = async () => {
  try {
    // 示例：跳转微信授权页面
    window.location.href = '/api/auth/wechat'
  } catch (err) {
    ElMessage.error('微信登录失败')
  }
}
</script>

<style scoped>
/* TAB 栏样式 */
.tab-switch {
  margin-bottom: 40px;
  text-align: center;
}

.tab-item {
  position: relative;
  display: inline-block;
  padding: 0 20px;
  font-size: 24px;
  font-weight: 700;
  color: #606266;
  text-decoration: none;
  transition: all 0.3s;
}

.tab-item.active {
  color: #3760f4;
}

.tab-item.active::after {
  content: '';
  position: absolute;
  bottom: -8px;
  left: 0;
  width: 100%;
  height: 2px;
  background: #3760f4;
}

/* 表单整体宽度 */
.login-form {
  max-width: 400px;
  margin: 0 auto;
}

.el-form-item {
  margin-bottom: 24px;
}

.el-input {
  height: 44px;
}

/* 使用深度选择器覆盖 el-input 内部 prepend 区域样式，确保垂直居中 */
:deep(.el-input__prepend) {
  display: flex;
  align-items: center;
  padding: 0;
}

/* 登录按钮样式 */
.login-buttons {
  display: flex;
  flex-direction: column;
  gap: 15px;
  margin-top: 30px;
  font-size: 16px;
}

.login-btn {
  background-color: #3760f4;
  font-size: 16px;
  height: 45.6px;
}

.wechat-btn {
  width: 100%;
  font-size: 16px;
  border-radius: 6px;
  height: 45.6px;
  margin: 0 !important;
}

/* 其他登录方式 */
.other-options {
  margin-top: 25px;
  display: flex;
  justify-content: space-between;
  width: 100%;
}

.login-link1 {
  cursor: pointer;
  color: #3760f4;
  margin-right: 30px;
}

.login-link2 {
  margin-right: auto; /* 占据剩余空间 */
}

.forgot-password {
  margin-left: auto; /* 推到最右侧 */
}

.other-options a {
  color: #3760f4;
  text-decoration: none;
}

/* 微信图标样式 */
.iconfont {
  font-family: 'iconfont' !important;
  font-size: 16px;
  font-style: normal;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

.icon-wechat:before {
  content: '\e65c';
}

/* 移除 Element Plus 默认按钮间距 */
:deep(.el-button + .el-button) {
  margin-left: 0;
}
</style>

'''

'''
<template>
  <div class="auth-form">
    <div class="tab-switch">
      <router-link to="/login" class="tab-item">登录</router-link>
      <router-link to="/register" class="tab-item active">注册</router-link>
    </div>

    <el-form :model="form" :rules="rules" class="register-form" ref="formRef">
      <el-form-item prop="username">
        <el-input v-model="form.username" type="text" placeholder="请输入用户名" />
      </el-form-item>
      <EmailVerification
        verify-type="register"
        v-model:email="form.email"
        v-model:code="form.code"
      />

      <el-form-item prop="password">
        <el-input v-model="form.password" type="password" placeholder="请输入密码" show-password />
      </el-form-item>

      <el-form-item prop="confirmPassword">
        <el-input
          v-model="form.confirmPassword"
          type="password"
          placeholder="请确认密码"
          show-password
        />
      </el-form-item>

      <el-form-item>
        <div class="agreement">
          <el-checkbox v-model="agreement" class="custom-checkbox">
            我已阅读并同意
            <router-link to="/agreement" class="link">《服务协议》</router-link>
            <router-link to="/privacy" class="link">《隐私政策》</router-link>
          </el-checkbox>
        </div>
      </el-form-item>

      <el-button type="primary" class="register-btn" @click="handleRegister">立即注册</el-button>
      <p class="already-have-account">
        已有账号？
        <router-link to="/login" class="login-link">点击登录</router-link>
      </p>
    </el-form>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import EmailVerification from '@/components/common/EmailVerification.vue'
import type { FormRules } from 'element-plus'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

const form = ref({
  username: '',
  email: '',
  code: '',
  password: '',
  confirmPassword: '',
})

const agreement = ref(true)

const validatePass2 = (_rule: unknown, value: string, callback: (error?: Error) => void) => {
  if (value !== form.value.password) {
    callback(new Error('两次输入密码不一致!'))
  } else {
    callback()
  }
}

const rules = ref<FormRules>({
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
  ],
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    {
      pattern: /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/,
      message: '邮箱格式不正确',
      trigger: 'blur',
    },
  ],
  code: [
    { required: true, message: '请输入验证码', trigger: 'blur' },
    { len: 6, message: '验证码为6位数字', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度6-20位', trigger: 'blur' },
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { validator: validatePass2, trigger: 'blur' },
  ],
})

const handleRegister = () => {
  // 验证表单
  formRef.value?.validate(async (valid: boolean) => {
    if (!valid) return
    if (!agreement.value) {
      ElMessage.warning('请先阅读并同意服务协议')
      return
    }

    try {
      const success = await userStore.register({
        username: form.value.username,
        email: form.value.email,
        code: form.value.code,
        password: form.value.password,
      })
      if (success) {
        ElMessage.success('注册成功，即将跳转到首页')
      }
    } catch (err: any) {
      ElMessage.error(err.message || '注册失败2')
    }
  })
}

// 添加表单引用
const formRef = ref()
</script>

<style scoped>
/* TAB 栏样式 */
.tab-switch {
  margin-bottom: 40px;
  text-align: center;
}

.tab-item {
  position: relative;
  display: inline-block;
  padding: 0 20px;
  font-size: 24px;
  font-weight: 700;
  color: #606266;
  text-decoration: none;
  transition: all 0.3s;
}

.tab-item.active {
  color: #3760f4;
}

.tab-item.active::after {
  content: '';
  position: absolute;
  bottom: -8px;
  left: 0;
  width: 100%;
  height: 2px;
  background: #3760f4;
}

/* 表单整体宽度 */
.register-form {
  max-width: 400px;
  margin: 0 auto;
}

/* 使用深度选择器覆盖 el-input 内部 prepend 区域样式，确保垂直居中 */
:deep(.el-input__prepend) {
  display: flex;
  align-items: center;
  padding: 0;
}

.register-btn {
  width: 100%;
  background-color: #3760f4;
  font-size: 16px;
  height: 50px;
}

.captcha-input {
  display: flex;
  width: 100%;
}

.captcha-button.is-disabled,
.captcha-button.is-disabled:focus,
.captcha-button.is-disabled:hover {
  width: 120px;
  height: 44px;
  background-color: aliceblue;
  color: #999999;
  cursor: not-allowed;
  background-image: none;
  background-color: #fff;
  border-color: #d7dae0;
}

.captcha-button {
  width: 120px;
  height: 44px;
  background-color: aliceblue;
  color: #999999;
  background-image: none;
  background-color: #fff;
  border-color: #d7dae0;
}

captcha-button:focus,
.captcha-button:hover {
  color: #3760f4;
  border-color: #c3cffc;
  background-color: #ebeffe;
  outline: 0;
}

.el-form-item {
  margin-bottom: 22px;
}

.el-input {
  height: 44px;
}

/* 协议条款样式 */
.agreement {
  font-size: 14px;
}

.agreement .link {
  color: #3760f4;
  text-decoration: none;
}

/* 复选框样式 */
:deep(.custom-checkbox .el-checkbox__label) {
  color: #606266;
}

:deep(.custom-checkbox .el-checkbox__input.is-checked + .el-checkbox__label) {
  color: #606266;
}

/* 已有账号样式 */
.already-have-account {
  margin-top: 15px;
  text-align: left;
  color: #606266;
}

.login-link {
  color: #3760f4;
  text-decoration: none;
  margin-left: 5px;
}
</style>

'''