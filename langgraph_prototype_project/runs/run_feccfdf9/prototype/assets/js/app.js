/**
 * 智能物流管理系统 - 公共交互脚本
 * 包含：菜单高亮、Toast提示、Modal弹窗、表单校验、按钮loading、URL参数读取、筛选重置等功能
 */

(function() {
  'use strict';

  // ==================== 全局配置 ====================
  window.AppConfig = {
    // 系统名称
    systemName: '智能物流管理系统',
    // 默认每页条数
    defaultPageSize: 10,
    // Toast显示时长(毫秒)
    toastDuration: 3000,
    // 菜单展开状态
    sidebarCollapsed: false
  };

  // ==================== 工具函数 ====================

  /**
   * 获取URL参数
   * @param {string} name 参数名
   * @returns {string|null} 参数值
   */
  window.getUrlParam = function(name) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(name);
  };

  /**
   * 获取URL所有参数
   * @returns {Object} 参数对象
   */
  window.getAllUrlParams = function() {
    const params = {};
    const urlParams = new URLSearchParams(window.location.search);
    urlParams.forEach((value, key) => {
      params[key] = value;
    });
    return params;
  };

  /**
   * 格式化日期
   * @param {string|Date} date 日期
   * @param {string} format 格式
   * @returns {string} 格式化后的日期
   */
  window.formatDate = function(date, format) {
    if (!date) return '-';
    const d = new Date(date);
    if (isNaN(d.getTime())) return '-';
    
    const year = d.getFullYear();
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    const hours = String(d.getHours()).padStart(2, '0');
    const minutes = String(d.getMinutes()).padStart(2, '0');
    const seconds = String(d.getSeconds()).padStart(2, '0');
    
    format = format || 'YYYY-MM-DD HH:mm:ss';
    return format
      .replace('YYYY', year)
      .replace('MM', month)
      .replace('DD', day)
      .replace('HH', hours)
      .replace('mm', minutes)
      .replace('ss', seconds);
  };

  /**
   * 格式化金额
   * @param {number} amount 金额
   * @returns {string} 格式化后的金额
   */
  window.formatMoney = function(amount) {
    if (amount === null || amount === undefined) return '¥0.00';
    return '¥' + Number(amount).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  };

  /**
   * 格式化状态显示
   * @param {string} status 状态码
   * @param {Object} statusMap 状态映射
   * @returns {string} 状态名称
   */
  window.formatStatus = function(status, statusMap) {
    const map = statusMap || window.AppConfig.statusMap || {};
    return map[status] || status || '-';
  };

  // ==================== Toast 提示 ====================

  /**
   * 显示Toast消息
   * @param {string} message 提示内容
   * @param {string} type 提示类型：success/error/warning/info
   * @param {number} duration 显示时长
   */
  window.showToast = function(message, type, duration) {
    type = type || 'info';
    duration = duration || AppConfig.toastDuration;
    
    // 移除已存在的toast
    const existingToast = document.querySelector('.toast-container');
    if (existingToast) {
      existingToast.remove();
    }
    
    // 创建toast容器
    const toast = document.createElement('div');
    toast.className = 'toast-container toast-' + type;
    toast.innerHTML = `
      <div class="toast-icon">
        ${getToastIcon(type)}
      </div>
      <div class="toast-message">${message}</div>
      <button class="toast-close">&times;</button>
    `;
    
    document.body.appendChild(toast);
    
    // 动画显示
    requestAnimationFrame(function() {
      toast.classList.add('toast-show');
    });
    
    // 关闭按钮
    toast.querySelector('.toast-close').addEventListener('click', function() {
      removeToast(toast);
    });
    
    // 自动关闭
    if (duration > 0) {
      setTimeout(function() {
        removeToast(toast);
      }, duration);
    }
  };

  function getToastIcon(type) {
    const icons = {
      success: '✓',
      error: '✕',
      warning: '⚠',
      info: 'ℹ'
    };
    return icons[type] || icons.info;
  }

  function removeToast(toast) {
    toast.classList.remove('toast-show');
    toast.classList.add('toast-hide');
    setTimeout(function() {
      if (toast.parentNode) {
        toast.parentNode.removeChild(toast);
      }
    }, 300);
  }

  // 快捷方法
  window.showSuccess = function(msg) { showToast(msg, 'success'); };
  window.showError = function(msg) { showToast(msg, 'error', 0); };
  window.showWarning = function(msg) { showToast(msg, 'warning'); };
  window.showInfo = function(msg) { showToast(msg, 'info'); };

  // ==================== Modal 弹窗 ====================

  /**
   * 打开Modal弹窗
   * @param {string} id 弹窗ID
   */
  window.openModal = function(id) {
    const modal = document.getElementById(id);
    if (!modal) return;
    
    modal.classList.add('modal-show');
    document.body.style.overflow = 'hidden';
    
    // 触发打开事件
    modal.dispatchEvent(new CustomEvent('modal:open'));
  };

  /**
   * 关闭Modal弹窗
   * @param {string} id 弹窗ID
   */
  window.closeModal = function(id) {
    const modal = document.getElementById(id);
    if (!modal) return;
    
    modal.classList.remove('modal-show');
    document.body.style.overflow = '';
    
    // 触发关闭事件
    modal.dispatchEvent(new CustomEvent('modal:close'));
  };

  /**
   * 确认框
   * @param {string} title 标题
   * @param {string} message 内容
   * @param {Function} onConfirm 确认回调
   * @param {Function} onCancel 取消回调
   */
  window.confirm = function(title, message, onConfirm, onCancel) {
    const confirmModal = document.getElementById('confirm-modal');
    if (!confirmModal) {
      // 如果没有确认框，模拟实现
      const confirmed = window.confirm(message);
      if (confirmed && onConfirm) {
        onConfirm();
      } else if (!confirmed && onCancel) {
        onCancel();
      }
      return;
    }
    
    confirmModal.querySelector('.modal-title').textContent = title;
    confirmModal.querySelector('.modal-body').textContent = message;
    
    const confirmBtn = confirmModal.querySelector('.btn-confirm');
    const cancelBtn = confirmModal.querySelector('.btn-cancel');
    
    // 清除旧的事件监听
    const newConfirmBtn = confirmBtn.cloneNode(true);
    confirmBtn.parentNode.replaceChild(newConfirmBtn, confirmBtn);
    
    const newCancelBtn = cancelBtn.cloneNode(true);
    cancelBtn.parentNode.replaceChild(newCancelBtn, cancelBtn);
    
    newConfirmBtn.addEventListener('click', function() {
      closeModal('confirm-modal');
      if (onConfirm) onConfirm();
    });
    
    newCancelBtn.addEventListener('click', function() {
      closeModal('confirm-modal');
      if (onCancel) onCancel();
    });
    
    openModal('confirm-modal');
  };

  // 初始化所有Modal的关闭按钮
  document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.modal').forEach(function(modal) {
      const closeBtn = modal.querySelector('.modal-close');
      if (closeBtn) {
        closeBtn.addEventListener('click', function() {
          modal.classList.remove('modal-show');
          document.body.style.overflow = '';
        });
      }
      
      // 点击遮罩关闭
      modal.addEventListener('click', function(e) {
        if (e.target === modal) {
          modal.classList.remove('modal-show');
          document.body.style.overflow = '';
        }
      });
    });
  });

  // ==================== 侧边栏 ====================

  /**
   * 切换侧边栏展开/收起
   */
  window.toggleSidebar = function() {
    const sidebar = document.querySelector('.sidebar');
    const main = document.querySelector('.main');
    const topbar = document.querySelector('.topbar');
    
    if (!sidebar) return;
    
    AppConfig.sidebarCollapsed = !AppConfig.sidebarCollapsed;
    
    if (AppConfig.sidebarCollapsed) {
      sidebar.classList.add('sidebar-collapsed');
      if (main) main.classList.add('main-expanded');
    } else {
      sidebar.classList.remove('sidebar-collapsed');
      if (main) main.classList.remove('main-expanded');
    }
    
    // 保存状态到localStorage
    try {
      localStorage.setItem('sidebarCollapsed', AppConfig.sidebarCollapsed);
    } catch (e) {}
  };

  /**
   * 初始化侧边栏状态
   */
  window.initSidebar = function() {
    try {
      const saved = localStorage.getItem('sidebarCollapsed');
      if (saved === 'true') {
        AppConfig.sidebarCollapsed = true;
        const sidebar = document.querySelector('.sidebar');
        const main = document.querySelector('.main');
        if (sidebar) sidebar.classList.add('sidebar-collapsed');
        if (main) main.classList.add('main-expanded');
      }
    } catch (e) {}
  };

  // ==================== 菜单高亮 ====================

  /**
   * 设置当前菜单高亮
   * @param {string} menuPath 菜单路径
   */
  window.setActiveMenu = function(menuPath) {
    // 清除所有高亮
    document.querySelectorAll('.nav-link').forEach(function(link) {
      link.classList.remove('active');
    });
    
    // 高亮当前菜单
    const activeLink = document.querySelector('.nav-link[href*="' + menuPath + '"]');
    if (activeLink) {
      activeLink.classList.add('active');
      
      // 展开父级菜单
      const parent = activeLink.closest('.nav-section');
      if (parent) {
        parent.classList.add('nav-section-open');
      }
    }
  };

  /**
   * 初始化菜单高亮（根据当前URL）
   */
  window.initMenuHighlight = function() {
    const path = window.location.pathname;
    const pageName = path.split('/').pop().replace('.html', '') || 'index';
    
    // 映射页面到菜单
    const pageToMenu = {
      'index': 'home',
      '首页': 'home',
      '订单列表': 'order-list',
      '订单详情': 'order-detail',
      '新建订单': 'order-create',
      '车辆管理': 'vehicle-list',
      '司机管理': 'driver-list',
      '智能调度': 'dispatch-center',
      '运输轨迹': 'transport-track',
      '异常处理': 'exception-list',
      '数据看板': 'data-board',
      '系统设置': 'system-settings'
    };
    
    const menuPath = pageToMenu[pageName] || pageName;
    window.setActiveMenu(menuPath);
  };

  // ==================== 表单校验 ====================

  /**
   * 校验表单
   * @param {string|HTMLElement} form 表单元素或选择器
   * @returns {boolean} 是否通过校验
   */
  window.validateRequired = function(form) {
    const formEl = typeof form === 'string' ? document.querySelector(form) : form;
    if (!formEl) return false;
    
    let isValid = true;
    const requiredFields = formEl.querySelectorAll('[required]');
    
    // 清除之前的错误状态
    formEl.querySelectorAll('.form-error').forEach(function(el) {
      el.classList.remove('form-error');
    });
    formEl.querySelectorAll('.error-message').forEach(function(el) {
      el.remove();
    });
    
    requiredFields.forEach(function(field) {
      const value = field.value.trim();
      const fieldName = field.name || field.dataset.label || '字段';
      
      if (!value) {
        isValid = false;
        showFieldError(field, fieldName + '不能为空');
      } else if (field.type === 'tel' || field.name === 'phone') {
        if (!/^1[3-9]\d{9}$/.test(value)) {
          isValid = false;
          showFieldError(field, '请输入正确的手机号');
        }
      } else if (field.type === 'email' || field.name === 'email') {
        if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
          isValid = false;
          showFieldError(field, '请输入正确的邮箱地址');
        }
      }
    });
    
    return isValid;
  };

  function showFieldError(field, message) {
    field.classList.add('form-error');
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message;
    field.parentNode.appendChild(errorDiv);
  }

  /**
   * 清除表单错误状态
   * @param {string|HTMLElement} form 表单元素或选择器
   */
  window.clearFormErrors = function(form) {
    const formEl = typeof form === 'string' ? document.querySelector(form) : form;
    if (!formEl) return;
    
    formEl.querySelectorAll('.form-error').forEach(function(el) {
      el.classList.remove('form-error');
    });
    formEl.querySelectorAll('.error-message').forEach(function(el) {
      el.remove();
    });
  };

  /**
   * 获取表单数据
   * @param {string|HTMLElement} form 表单元素或选择器
   * @returns {Object} 表单数据对象
   */
  window.getFormData = function(form) {
    const formEl = typeof form === 'string' ? document.querySelector(form) : form;
    if (!formEl) return {};
    
    const data = {};
    const formData = new FormData(formEl);
    
    formData.forEach(function(value, key) {
      // 处理同名多选框
      if (data[key]) {
        if (Array.isArray(data[key])) {
          data[key].push(value);
        } else {
          data[key] = [data[key], value];
        }
      } else {
        data[key] = value;
      }
    });
    
    return data;
  };

  // ==================== 按钮Loading ====================

  /**
   * 带Loading的提交
   * @param {HTMLElement} button 按钮元素
   * @param {Function} callback 提交回调
   * @returns {Promise}
   */
  window.submitWithLoading = function(button, callback) {
    if (!button) return Promise.reject('Button not found');
    
    const originalText = button.textContent;
    const originalDisabled = button.disabled;
    
    // 设置loading状态
    button.disabled = true;
    button.classList.add('btn-loading');
    button.innerHTML = '<span class="btn-spinner"></span> 处理中...';
    
    try {
      const result = callback();
      
      // 如果是Promise
      if (result && typeof result.then === 'function') {
        return result
          .then(function(data) {
            resetButton();
            return data;
          })
          .catch(function(error) {
            resetButton();
            throw error;
          });
      } else {
        resetButton();
        return Promise.resolve(result);
      }
    } catch (error) {
      resetButton();
      return Promise.reject(error);
    }
    
    function resetButton() {
      button.disabled = originalDisabled;
      button.classList.remove('btn-loading');
      button.textContent = originalText;
    }
  };

  // ==================== 订单操作 ====================

  /**
   * 订单派单
   * @param {string} orderId 订单ID
   * @param {Object} data 派单数据
   */
  window.dispatchOrder = function(orderId, data) {
    return new Promise(function(resolve, reject) {
      window.submitWithLoading(document.querySelector('.btn-dispatch'), function() {
        // 模拟API调用
        setTimeout(function() {
          if (Math.random() > 0.1) {
            window.showSuccess('派单成功，订单已分配');
            
          // 模拟司机收到通知
          setTimeout(function() {
            alert('司机收到新任务通知：\n订单号：' + orderId + '\n路线：' + (data.from || '发货地') + ' → ' + (data.to || '收货地') + '\n车辆：' + (data.vehicle || '京A12345') + '\n司机：' + (data.driver || '张三'));
          }, 500);
          
          resolve({ success: true, orderId: orderId });
          } else {
            reject(new Error('派单失败：车辆已被占用'));
          }
        }, 1000);
      });
    });
  };

  /**
   * 订单签收
   * @param {string} orderId 订单ID
   * @param {Object} data 签收数据
   */
  window.signOrder = function(orderId, data) {
    return window.submitWithLoading(document.querySelector('.btn-sign'), function() {
      return new Promise(function(resolve, reject) {
        setTimeout(function() {
          window.showSuccess('签收成功');
          resolve({ success: true, orderId: orderId });
        }, 800);
      });
    });
  };

  /**
   * 订单取消
   * @param {string} orderId 订单ID
   * @param {string} reason 取消原因
   */
  window.cancelOrder = function(orderId, reason) {
    return window.submitWithLoading(document.querySelector('.btn-cancel'), function() {
      return new Promise(function(resolve, reject) {
        setTimeout(function() {
          window.showSuccess('订单已取消');
          resolve({ success: true, orderId: orderId });
        }, 500);
      });
    });
  };

  // ==================== 车辆操作 ====================

  /**
   * 新增车辆
   * @param {Object} data 车辆数据
   */
  window.addVehicle = function(data) {
    return window.submitWithLoading(document.querySelector('.btn-submit'), function() {
      return new Promise(function(resolve, reject) {
        setTimeout(function() {
          window.showSuccess('车辆添加成功');
          resolve({ success: true });
        }, 800);
      });
    });
  };

  /**
   * 编辑车辆
   * @param {string} vehicleId 车辆ID
   * @param {Object} data 车辆数据
   */
  window.updateVehicle = function(vehicleId, data) {
    return window.submitWithLoading(document.querySelector('.btn-submit'), function() {
      return new Promise(function(resolve, reject) {
        setTimeout(function() {
          window.showSuccess('车辆信息更新成功');
          resolve({ success: true, vehicleId: vehicleId });
        }, 800);
      });
    });
  };

  /**
   * 删除车辆
   * @param {string} vehicleId 车辆ID
   */
  window.deleteVehicle = function(vehicleId) {
    return new Promise(function(resolve, reject) {
      window.confirm(
        '确认删除',
        '确定要删除该车辆吗？此操作不可恢复。',
        function() {
          window.submitWithLoading(document.querySelector('.btn-delete'), function() {
            return new Promise(function(resolve, reject) {
              setTimeout(function() {
                window.showSuccess('车辆删除成功');
                resolve({ success: true });
              }, 500);
            });
          });
        }
      );
    });
  };

  // ==================== 司机操作 ====================

  /**
   * 新增司机
   * @param {Object} data 司机数据
   */
  window.addDriver = function(data) {
    return window.submitWithLoading(document.querySelector('.btn-submit'), function() {
      return new Promise(function(resolve, reject) {
        setTimeout(function() {
          window.showSuccess('司机添加成功');
          resolve({ success: true });
        }, 800);
      });
    });
  };

  /**
   * 删除司机
   * @param {string} driverId 司机ID
   */
  window.deleteDriver = function(driverId) {
    return new Promise(function(resolve, reject) {
      window.confirm(
        '确认删除',
        '确定要删除该司机吗？',
        function() {
          window.submitWithLoading(document.querySelector('.btn-delete'), function() {
            return new Promise(function(resolve, reject) {
              setTimeout(function() {
                window.showSuccess('司机删除成功');
                resolve({ success: true });
              }, 500);
            });
          });
        }
      );
    });
  };

  // ==================== 智能调度 ====================

  /**
   * 智能派单
   * @param {Array} orderIds 订单ID数组
   */
  window.smartDispatch = function(orderIds) {
    return window.submitWithLoading(document.querySelector('.btn-smart-dispatch'), function() {
      return new Promise(function(resolve, reject) {
        setTimeout(function() {
          // 显示智能推荐方案
          const recommendation = {
            'ORD001': { vehicle: '京A12345', driver: '张三', matchScore: 95 },
            'ORD002': { vehicle: '京B67890', driver: '李四', matchScore: 88 }
          };
          
          let msg = '智能派单成功！\n';
          orderIds.forEach(function(id) {
            const rec = recommendation[id] || {};
            msg += '\n订单 ' + id + ': 分配给 ' + (rec.vehicle || '待分配') + ' / ' + (rec.driver || '待分配') + ' (匹配度: ' + (rec.matchScore || '-') + '%)';
          });
          
          window.showSuccess('智能派单完成');
          alert(msg);
          resolve({ success: true, recommendation: recommendation });
        }, 1500);
      });
    });
  };

  /**
   * 撤销派单
   * @param {string} orderId 订单ID
   */
  window.revokeDispatch = function(orderId) {
    return new Promise(function(resolve, reject) {
      window.confirm(
        '确认撤销',
        '确定要撤销该订单的派单吗？撤销后订单将恢复为待派单状态。',
        function() {
          window.submitWithLoading(document.querySelector('.btn-revoke'), function() {
            return new Promise(function(resolve, reject) {
              setTimeout(function() {
                window.showSuccess('撤销成功，订单已恢复为待派单');
                resolve({ success: true });
              }, 500);
            });
          });
        }
      );
    });
  };

  // ==================== 异常处理 ====================

  /**
   * 上报异常
   * @param {Object} data 异常数据
   */
  window.reportException = function(data) {
    return window.submitWithLoading(document.querySelector('.btn-submit'), function() {
      return new Promise(function(resolve, reject) {
        setTimeout(function() {
          window.showSuccess('异常已上报');
          resolve({ success: true });
        }, 800);
      });
    });
  };

  /**
   * 处理异常
   * @param {string} exceptionId 异常ID
   * @param {Object} data 处理数据
   */
  window.handleException = function(exceptionId, data) {
    return window.submitWithLoading(document.querySelector('.btn-handle'), function() {
      return new Promise(function(resolve, reject) {
        setTimeout(function() {
          window.showSuccess('异常处理完成');
          resolve({ success: true });
        }, 800);
      });
    });
  };

  /**
   * 异常升级
   * @param {string} exceptionId 异常ID
   */
  window.escalateException = function(exceptionId) {
    return new Promise(function(resolve, reject) {
      window.confirm(
        '确认升级',
        '确定要将该异常升级至管理层处理吗？',
        function() {
          window.submitWithLoading(document.querySelector('.btn-escalate'), function() {
            return new Promise(function(resolve, reject) {
              setTimeout(function() {
                window.showSuccess('异常已升级');
                resolve({ success: true });
              }, 500);
            });
          });
        }
      );
    });
  };

  // ==================== 数据导出 ====================

  /**
   * 导出数据
   * @param {string} type 导出类型
   * @param {Object} params 导出参数
   */
  window.exportData = function(type, params) {
    const exportBtn = document.querySelector('.btn-export');
    if (!exportBtn) {
      window.showWarning('导出功能初始化中...');
      return;
    }
    
    return window.submitWithLoading(exportBtn, function() {
      return new Promise(function(resolve, reject) {
        setTimeout(function() {
          window.showSuccess(type + '数据导出成功');
          resolve({ success: true, fileName: type + '_' + window.formatDate(new Date(), 'YYYYMMDD') + '.xlsx' });
        }, 1000);
      });
    });
  };

  // ==================== 数据导入 ====================

  /**
   * 导入数据
   * @param {string} type 导入类型
   * @param {File} file 文件
   */
  window.importData = function(type, file) {
    return new Promise(function(resolve, reject) {
      // 模拟导入过程
      window.showInfo('正在解析文件...');
      
      setTimeout(function() {
        // 模拟导入结果
        const successCount = Math.floor(Math.random() * 10) + 5;
        const failCount = Math.floor(Math.random() * 3);
        
        if (failCount > 0) {
          window.showWarning('导入完成：成功 ' + successCount + ' 条，失败 ' + failCount + ' 条');
        } else {
          window.showSuccess('导入成功：共 ' + successCount + ' 条数据');
        }
        
        resolve({ 
          success: true, 
          successCount: successCount,
          failCount: failCount 
        });
      }, 1500);
    });
  };

  // ==================== 筛选与重置 ====================

  /**
   * 筛选列表
   * @param {string} listSelector 列表选择器
   * @param {Function} filterFn 筛选函数
   */
  window.filterList = function(listSelector, filterFn) {
    const list = document.querySelector(listSelector);
    if (!list) return;
    
    const items = list.querySelectorAll('.list-item, tr');
    let visibleCount = 0;
    
    items.forEach(function(item) {
      const shouldShow = filterFn(item);
      if (shouldShow) {
        item.style.display = '';
        visibleCount++;
      } else {
        item.style.display = 'none';
      }
    });
    
    // 显示空状态
    const emptyState = list.querySelector('.empty-state');
    if (emptyState) {
      emptyState.style.display = visibleCount === 0 ? 'flex' : 'none';
    }
    
    // 显示结果数量
    const countTip = document.querySelector('.filter-result-count');
    if (countTip) {
      countTip.textContent = '找到 ' + visibleCount + ' 条结果';
    }
    
    return visibleCount;
  };

  /**
   * 重置筛选
   * @param {string} formSelector 表单选择器
   * @param {string} listSelector 列表选择器
   */
  window.resetFilter = function(formSelector, listSelector) {
    const form = document.querySelector(formSelector);
    if (form) {
      form.reset();
      window.clearFormErrors(form);
    }
    
    // 显示所有项
    const list = document.querySelector(listSelector);
    if (list) {
      list.querySelectorAll('.list-item, tr').forEach(function(item) {
        item.style.display = '';
      });
      
      const emptyState = list.querySelector('.empty-state');
      if (emptyState) {
        emptyState.style.display = 'none';
      }
    }
    
    const countTip = document.querySelector('.filter-result-count');
    if (countTip) {
      countTip.textContent = '';
    }
  };

  // ==================== 运输轨迹 ====================

  /**
   * 开始轨迹回放
   * @param {Array} trackPoints 轨迹点数组
   */
  window.startTrackPlayback = function(trackPoints) {
    const playBtn = document.querySelector('.btn-play');
    const progressBar = document.querySelector('.playback-progress');
    
    if (!playBtn || !trackPoints || trackPoints.length === 0) {
      window.showWarning('无轨迹数据');
      return;
    }
    
    let currentIndex = 0;
    
    function playNext() {
      if (currentIndex >= trackPoints.length) {
        window.showInfo('轨迹回放完成');
        return;
      }
      
      const point = trackPoints[currentIndex];
      
      // 更新进度条
      if (progressBar) {
        progressBar.style.width = ((currentIndex + 1) / trackPoints.length * 100) + '%';
      }
      
      // 更新地图位置（模拟）
      console.log('当前位置:', point.latitude, point.longitude, point.locationTime);
      
      currentIndex++;
      
      // 模拟间隔
      setTimeout(playNext, 1000);
    }
    
    playBtn.classList.add('playing');
    playBtn.textContent = '暂停';
    window.showInfo('开始轨迹回放');
    playNext();
  };

  /**
   * 刷新车辆位置
   */
  window.refreshVehicleLocation = function() {
    window.showInfo('正在刷新位置...');
    
    setTimeout(function() {
      window.showSuccess('位置已更新');
    }, 800);
  };

  // ==================== 分页 ====================

  /**
   * 跳转到指定页
   * @param {number} page 页码
   * @param {Function} callback 回调函数
   */
  window.goToPage = function(page, callback) {
    if (callback) {
      callback(page);
    }
    
    // 滚动到顶部
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  // ==================== 权限提示 ====================

  /**
   * 显示权限不足提示
   * @param {string} action 操作名称
   */
  window.showPermissionDenied = function(action) {
    window.showWarning('您没有执行「' + action + '」的权限');
  };

  /**
   * 检查权限
   * @param {string} permission 权限标识
   * @returns {boolean} 是否有权限
   */
  window.checkPermission = function(permission) {
    // 从页面获取当前用户角色
    const currentRole = document.body.dataset.role || '调度员';
    
    const rolePermissions = {
      '管理人员': ['view', 'dispatch', 'export', 'approve', 'manage'],
      '调度员': ['view', 'dispatch', 'handle_exception'],
      '运营人员': ['view', 'create_order', 'track'],
      '司机': ['view_task', 'report_exception'],
      '车辆管理人员': ['view', 'manage_vehicle']
    };
    
    const permissions = rolePermissions[currentRole] || [];
    return permissions.includes(permission) || permissions.includes('view');
  };

  // ==================== 初始化 ====================

  document.addEventListener('DOMContentLoaded', function() {
    // 初始化侧边栏
    window.initSidebar();
    
    // 初始化菜单高亮
    window.initMenuHighlight();
    
    // 绑定侧边栏toggle按钮
    const toggleBtn = document.querySelector('.sidebar-toggle');
    if (toggleBtn) {
      toggleBtn.addEventListener('click', window.toggleSidebar);
    }
    
    // 绑定筛选表单提交
    document.querySelectorAll('.filter-form').forEach(function(form) {
      form.addEventListener('submit', function(e) {
        e.preventDefault();
        // 由页面自行处理筛选逻辑
        form.dispatchEvent(new CustomEvent('filter:submit'));
      });
    });
    
    // 绑定重置按钮
    document.querySelectorAll('.btn-reset').forEach(function(btn) {
      btn.addEventListener('click', function() {
        const form = btn.closest('form') || document.querySelector('.filter-form');
        if (form) {
          form.reset();
          form.dispatchEvent(new CustomEvent('filter:reset'));
        }
      });
    });
    
    // 绑定返回按钮
    document.querySelectorAll('.btn-back').forEach(function(btn) {
      btn.addEventListener('click', function() {
        if (window.history.length > 1) {
          window.history.back();
        } else {
          window.location.href = './index.html';
        }
      });
    });
    
    // 绑定Tab切换
    document.querySelectorAll('.tab-item').forEach(function(tab) {
      tab.addEventListener('click', function() {
        const tabGroup = tab.closest('.tabs');
        const targetTab = tab.dataset.tab;
        
        // 移除active
        tabGroup.querySelectorAll('.tab-item').forEach(function(t) {
          t.classList.remove('active');
        });
        tabGroup.querySelectorAll('.tab-content').forEach(function(c) {
          c.classList.remove('active');
        });
        
        // 添加active
        tab.classList.add('active');
        const content = document.getElementById(targetTab);
        if (content) {
          content.classList.add('active');
        }
      });
    });
    
    console.log('智能物流管理系统 - 公共脚本已加载');
  });

  // ==================== 导出 ====================

  window.App = {
    config: AppConfig,
    getUrlParam: window.getUrlParam,
    getAllUrlParams: window.getAllUrlParams,
    formatDate: window.formatDate,
    formatMoney: window.formatMoney,
    formatStatus: window.formatStatus,
    showToast: window.showToast,
    showSuccess: window.showSuccess,
    showError: window.showError,
    showWarning: window.showWarning,
    showInfo: window.showInfo,
    openModal: window.openModal,
    closeModal: window.closeModal,
    confirm: window.confirm,
    toggleSidebar: window.toggleSidebar,
    setActiveMenu: window.setActiveMenu,
    validateRequired: window.validateRequired,
    clearFormErrors: window.clearFormErrors,
    getFormData: window.getFormData,
    submitWithLoading: window.submitWithLoading,
    dispatchOrder: window.dispatchOrder,
    signOrder: window.signOrder,
    cancelOrder: window.cancelOrder,
    addVehicle: window.addVehicle,
    updateVehicle: window.updateVehicle,
    deleteVehicle: window.deleteVehicle,
    addDriver: window.addDriver,
    deleteDriver: window.deleteDriver,
    smartDispatch: window.smartDispatch,
    revokeDispatch: window.revokeDispatch,
    reportException: window.reportException,
    handleException: window.handleException,
    escalateException: window.escalateException,
    exportData: window.exportData,
    importData: window.importData,
    filterList: window.filterList,
    resetFilter: window.resetFilter,
    startTrackPlayback: window.startTrackPlayback,
    refreshVehicleLocation: window.refreshVehicleLocation,
    goToPage: window.goToPage,
    showPermissionDenied: window.showPermissionDenied,
    checkPermission: window.checkPermission
  };

})();