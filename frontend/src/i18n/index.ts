import { createI18n } from 'vue-i18n'

const messages = {
  'zh-CN': {
    common: {
      dashboard: '总览', books: '图书', borrow: '借还', users: '读者', login: '登录', logout: '退出登录'
    }
  }
}

const i18n = createI18n({
  legacy: false,
  locale: 'zh-CN',
  messages
})

export default i18n
