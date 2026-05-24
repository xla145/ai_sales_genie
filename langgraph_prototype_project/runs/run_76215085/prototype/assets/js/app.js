/**
 * 智能物流管理系统 - 公共交互脚本
 * 包含：菜单高亮、Toast、Modal、校验、筛选、分页等功能
 */

(function() {
  'use strict';

  // ============================================
  // 全局状态管理
  // ============================================
  const AppState = {
    currentPage: 1,
    pageSize: 20,
    total: 0,
    currentRole: 'dispatcher', // 调度员
    filters: {},
    orderStatusFilter: 'all',
    vehicleStatusFilter: 'all',
    driverStatusFilter: 'all',
    selectedOrder: null,
    selectedVehicle: null,
    selectedDriver: null
  };

  // ============================================
  // 初始化入口
  // ============================================
  document.addEventListener('DOMContentLoaded', function() {
    initMenuHighlight();
    initSidebarToggle();
    initToasts();
    initModals();
    initForms();
    initFilters();
    initPagination();
    initTableRows();
    initOrderActions();
    initVehicleActions();
    initDriverActions();
    initDispatchActions();
    initTrackActions();
    initExceptionActions();
    initHomeActions();
    initDataExport();
    initUserMenu();
  });;

  // ============================================
  // 菜单高亮
  // ============================================
  function initMenuHighlight() {
    const navLinks = document.querySelectorAll('.nav-link');
    const currentPath = window.location.pathname;
    const pageName = currentPath.split('/').pop().replace('.html', '');

    navLinks.forEach(link => {
      const href = link.getAttribute('href');
      if (href && (href.includes(pageName) || (pageName === '' && href.includes('index.html')))) {
        link.classList.add('active');
      }
    });
  }

  // ============================================
  // 侧边栏折叠
  // ============================================
  function initSidebarToggle() {
    const toggleBtn = document.querySelector('.sidebar-toggle');
    const sidebar = document.querySelector('.sidebar');
    const main = document.querySelector('.main');

    if (toggleBtn && sidebar) {
      toggleBtn.addEventListener('click', function() {
        sidebar.classList.toggle('collapsed');
        main.classList.toggle('expanded');
      });
    }
  }

  // ============================================
  // Toast 提示
  // ============================================
  function initToasts() {
    window.showToast = function(message, type, duration) {
      type = type || 'info';
      duration = duration || 3000;

      let container = document.querySelector('.toast-container');
      if (!container) {
        container = document.createElement('div');
        container.className = 'toast-container';
        document.body.appendChild(container);
      }

      const toast = document.createElement('div');
      toast.className = 'toast toast-' + type;

      const icons = {
        success: '✓',
        error: '✕',
        warning: '⚠',
        info: 'ℹ'
      };

      toast.innerHTML = `
        <span class="toast-icon">${icons[type] || icons.info}</span>
        <span class="toast-message">${message}</span>
        <button class="toast-close">&times;</button>
      `;

      container.appendChild(toast);

      // 动画
      setTimeout(() => toast.classList.add('show'), 10);

      // 关闭按钮
      const closeBtn = toast.querySelector('.toast-close');
      closeBtn.addEventListener('click', () => removeToast(toast));

      // 自动关闭
      setTimeout(() => removeToast(toast), duration);

      function removeToast(el) {
        el.classList.remove('show');
        setTimeout(() => el.remove(), 300);
      }
    };
  }

  // ============================================
  // Modal 弹窗
  // ============================================
  function initModals() {
    window.openModal = function(modalId) {
      const modal = document.getElementById(modalId);
      if (modal) {
        modal.classList.add('show');
        document.body.style.overflow = 'hidden';

        // 点击遮罩关闭
        modal.addEventListener('click', function(e) {
          if (e.target === modal) {
            closeModal(modalId);
          }
        });
      }
    };

    window.closeModal = function(modalId) {
      const modal = document.getElementById(modalId);
      if (modal) {
        modal.classList.remove('show');
        document.body.style.overflow = '';
      }
    };

    // 关闭按钮
    document.querySelectorAll('.modal-close, .modal-cancel').forEach(btn => {
      btn.addEventListener('click', function() {
        const modal = this.closest('.modal');
        if (modal) {
          closeModal(modal.id);
        }
      });
    });
  }

  // ============================================
  // 表单验证与提交
  // ============================================
  function initForms() {
    window.validateRequired = function(form) {
      const requiredFields = form.querySelectorAll('[required]');
      let isValid = true;
      let firstError = null;

      requiredFields.forEach(field => {
        const value = field.value.trim();
        const errorMsg = field.nextElementSibling;

        if (!value) {
          isValid = false;
          field.classList.add('error');

          if (!errorMsg || !errorMsg.classList.contains('error-message')) {
            const msg = document.createElement('span');
            msg.className = 'error-message';
            msg.textContent = '此项为必填项';
            field.parentNode.insertBefore(msg, field.nextSibling);
          }

          if (!firstError) firstError = field;
        } else {
          field.classList.remove('error');
          if (errorMsg && errorMsg.classList.contains('error-message')) {
            errorMsg.remove();
          }
        }
      });

      // 手机号验证
      const phoneFields = form.querySelectorAll('input[type="tel"][required]');
      phoneFields.forEach(field => {
        const value = field.value.trim();
        const phoneRegex = /^1[3-9]\d{9}$/;
        const errorMsg = field.nextElementSibling;

        if (value && !phoneRegex.test(value)) {
          isValid = false;
          field.classList.add('error');

          if (!errorMsg || !errorMsg.classList.contains('error-message')) {
            const msg = document.createElement('span');
            msg.className = 'error-message';
            msg.textContent = '请输入正确的手机号';
            field.parentNode.insertBefore(msg, field.nextSibling);
          }

          if (!firstError) firstError = field;
        }
      });

      if (firstError) {
        firstError.focus();
      }

      return isValid;
    };

    window.submitWithLoading = function(button, callback) {
      const originalText = button.textContent;
      button.classList.add('loading');
      button.disabled = true;
      button.innerHTML = '<span class="loading-spinner"></span> 处理中...';

      setTimeout(() => {
        try {
          const result = callback();
          if (result !== false) {
            button.classList.remove('loading');
            button.disabled = false;
            button.textContent = originalText;
          }
        } catch (e) {
          button.classList.remove('loading');
          button.disabled = false;
          button.textContent = originalText;
          showToast('操作失败: ' + e.message, 'error');
        }
      }, 800);
    };

    // 表单失焦校验
    document.querySelectorAll('input[required], select[required]').forEach(field => {
      field.addEventListener('blur', function() {
        if (!this.value.trim()) {
          this.classList.add('error');
        } else {
          this.classList.remove('error');
          const errorMsg = this.nextElementSibling;
          if (errorMsg && errorMsg.classList.contains('error-message')) {
            errorMsg.remove();
          }
        }
      });
    });
  }

  // ============================================
  // 筛选功能
  // ============================================
  function initFilters() {
    // 订单筛选
    const orderStatusFilter = document.getElementById('orderStatusFilter');
    if (orderStatusFilter) {
      orderStatusFilter.addEventListener('change', function() {
        AppState.orderStatusFilter = this.value;
        filterOrders();
      });
    }

    // 订单搜索
    const orderSearchBtn = document.getElementById('orderSearchBtn');
    if (orderSearchBtn) {
      orderSearchBtn.addEventListener('click', function() {
        filterOrders();
      });
    }

    // 订单重置
    const orderResetBtn = document.getElementById('orderResetBtn');
    if (orderResetBtn) {
      orderResetBtn.addEventListener('click', function() {
        document.getElementById('orderStatusFilter').value = 'all';
        document.getElementById('orderKeyword').value = '';
        AppState.orderStatusFilter = 'all';
        AppState.currentPage = 1;
        filterOrders();
      });
    }

    // 车辆筛选
    const vehicleStatusFilter = document.getElementById('vehicleStatusFilter');
    if (vehicleStatusFilter) {
      vehicleStatusFilter.addEventListener('change', function() {
        AppState.vehicleStatusFilter = this.value;
        filterVehicles();
      });
    }

    // 车辆搜索
    const vehicleSearchBtn = document.getElementById('vehicleSearchBtn');
    if (vehicleSearchBtn) {
      vehicleSearchBtn.addEventListener('click', function() {
        filterVehicles();
      });
    }

    // 司机筛选
    const driverStatusFilter = document.getElementById('driverStatusFilter');
    if (driverStatusFilter) {
      driverStatusFilter.addEventListener('change', function() {
        AppState.driverStatusFilter = this.value;
        filterDrivers();
      });
    }

    // 司机搜索
    const driverSearchBtn = document.getElementById('driverSearchBtn');
    if (driverSearchBtn) {
      driverSearchBtn.addEventListener('click', function() {
        filterDrivers();
      });
    }
  }

  // 订单筛选
  function filterOrders() {
    const rows = document.querySelectorAll('#orderTableBody tr');
    const status = AppState.orderStatusFilter;
    const keyword = document.getElementById('orderKeyword')?.value.toLowerCase() || '';

    rows.forEach(row => {
      const rowStatus = row.dataset.status;
      const text = row.textContent.toLowerCase();

      const statusMatch = status === 'all' || rowStatus === status;
      const keywordMatch = !keyword || text.includes(keyword);

      row.style.display = (statusMatch && keywordMatch) ? '' : 'none';
    });

    showToast('筛选完成', 'success');
  }

  // 车辆筛选
  function filterVehicles() {
    const rows = document.querySelectorAll('#vehicleTableBody tr');
    const status = AppState.vehicleStatusFilter;

    rows.forEach(row => {
      const rowStatus = row.dataset.status;
      row.style.display = (status === 'all' || rowStatus === status) ? '' : 'none';
    });

    showToast('筛选完成', 'success');
  }

  // 司机筛选
  function filterDrivers() {
    const rows = document.querySelectorAll('#driverTableBody tr');
    const status = AppState.driverStatusFilter;

    rows.forEach(row => {
      const rowStatus = row.dataset.status;
      row.style.display = (status === 'all' || rowStatus === status) ? '' : 'none';
    });

    showToast('筛选完成', 'success');
  }

  // ============================================
  // 分页功能
  // ============================================
  function initPagination() {
    const pageItems = document.querySelectorAll('.pagination .page-item');
    pageItems.forEach(item => {
      item.addEventListener('click', function() {
        const page = this.dataset.page;
        if (page) {
          goToPage(parseInt(page));
        }
      });
    });

    // 每页条数切换
    const pageSizeSelect = document.getElementById('pageSizeSelect');
    if (pageSizeSelect) {
      pageSizeSelect.addEventListener('change', function() {
        AppState.pageSize = parseInt(this.value);
        AppState.currentPage = 1;
        updatePagination();
      });
    }
  }

  function goToPage(page) {
    AppState.currentPage = page;
    updatePagination();
    showToast('加载第 ' + page + ' 页', 'info');
  }

  function updatePagination() {
    const pageItems = document.querySelectorAll('.pagination .page-item');
    pageItems.forEach(item => {
      const page = item.dataset.page;
      if (page == AppState.currentPage) {
        item.classList.add('active');
      } else {
        item.classList.remove('active');
      }
    });
  }

  // ============================================
  // 表格行交互
  // ============================================
  function initTableRows() {
    // 订单行点击
    document.querySelectorAll('.order-row').forEach(row => {
      row.addEventListener('click', function() {
        const orderId = this.dataset.orderId;
        if (orderId) {
          window.location.href = './订单详情.html?id=' + orderId;
        }
      });
    });

    // 车辆行点击
    document.querySelectorAll('.vehicle-row').forEach(row => {
      row.addEventListener('click', function() {
        const vehicleId = this.dataset.vehicleId;
        if (vehicleId) {
          window.location.href = './车辆管理详情.html?id=' + vehicleId;
        }
      });
    });

    // 司机行点击
    document.querySelectorAll('.driver-row').forEach(row => {
      row.addEventListener('click', function() {
        const driverId = this.dataset.driverId;
        if (driverId) {
          window.location.href = './司机管理详情.html?id=' + driverId;
        }
      });
    });
  }

  // ============================================
  // 订单操作
  // ============================================
  function initOrderActions() {
    // 新建订单
    const newOrderBtn = document.getElementById('newOrderBtn');
    if (newOrderBtn) {
      newOrderBtn.addEventListener('click', function() {
        window.location.href = './新建订单.html';
      });
    }

    // 订单详情
    document.querySelectorAll('.view-order').forEach(btn => {
      btn.addEventListener('click', function(e) {
        e.stopPropagation();
        const orderId = this.dataset.orderId;
        window.location.href = './订单详情.html?id=' + orderId;
      });
    });

    // 订单派单
    document.querySelectorAll('.dispatch-order').forEach(btn => {
      btn.addEventListener('click', function(e) {
        e.stopPropagation();
        const orderId = this.dataset.orderId;
        window.location.href = './智能调度.html?orderId=' + orderId;
      });
    });

    // 订单取消
    document.querySelectorAll('.cancel-order').forEach(btn => {
      btn.addEventListener('click', function(e) {
        e.stopPropagation();
        const orderId = this.dataset.orderId;
        if (confirm('确定要取消该订单吗？')) {
          showToast('订单已取消', 'success');
          setTimeout(() => {
            window.location.reload();
          }, 1000);
        }
      });
    });

    // 提交新建订单
    const submitOrderBtn = document.getElementById('submitOrderBtn');
    if (submitOrderBtn) {
      submitOrderBtn.addEventListener('click', function() {
        const form = document.getElementById('orderForm');
        if (validateRequired(form)) {
          submitWithLoading(this, function() {
            showToast('订单创建成功', 'success');
            setTimeout(() => {
              window.location.href = './订单列表.html';
            }, 1500);
          });
        }
      });
    }

    // 订单详情页操作
    const editOrderBtn = document.getElementById('editOrderBtn');
    if (editOrderBtn) {
      editOrderBtn.addEventListener('click', function() {
        openModal('editOrderModal');
      });
    }

    const smartDispatchBtn = document.getElementById('smartDispatchBtn');
    if (smartDispatchBtn) {
      smartDispatchBtn.addEventListener('click', function() {
        openModal('smartDispatchModal');
      });
    }

    const manualDispatchBtn = document.getElementById('manualDispatchBtn');
    if (manualDispatchBtn) {
      manualDispatchBtn.addEventListener('click', function() {
        openModal('manualDispatchModal');
      });
    }

    // 智能派单确认
    const confirmSmartDispatch = document.getElementById('confirmSmartDispatch');
    if (confirmSmartDispatch) {
      confirmSmartDispatch.addEventListener('click', function() {
        submitWithLoading(this, function() {
          closeModal('smartDispatchModal');
          showToast('派单成功', 'success');
        });
      });
    }

    // 手动派单确认
    const confirmManualDispatch = document.getElementById('confirmManualDispatch');
    if (confirmManualDispatch) {
      confirmManualDispatch.addEventListener('click', function() {
        const vehicleSelect = document.getElementById('selectVehicle');
        const driverSelect = document.getElementById('selectDriver');

        if (!vehicleSelect.value || !driverSelect.value) {
          showToast('请选择车辆和司机', 'warning');
          return false;
        }

        submitWithLoading(this, function() {
          closeModal('manualDispatchModal');
          showToast('派单成功', 'success');
        });
      });
    }

    // 复制订单
    const copyOrderBtn = document.getElementById('copyOrderBtn');
    if (copyOrderBtn) {
      copyOrderBtn.addEventListener('click', function() {
        showToast('订单已复制，请完善信息', 'success');
        setTimeout(() => {
          window.location.href = './新建订单.html?copy=true';
        }, 1000);
      });
    }

    // 查看轨迹
    const viewTrackBtn = document.getElementById('viewTrackBtn');
    if (viewTrackBtn) {
      viewTrackBtn.addEventListener('click', function() {
        const orderId = this.dataset.orderId || '';
        window.location.href = './运输轨迹.html?orderId=' + orderId;
      });
    }

    // 签收确认
    const confirmSignBtn = document.getElementById('confirmSignBtn');
    if (confirmSignBtn) {
      confirmSignBtn.addEventListener('click', function() {
        if (confirm('确认货物已签收吗？')) {
          showToast('签收确认成功', 'success');
          setTimeout(() => {
            window.location.reload();
          }, 1000);
        }
      });
    }
  }

  // ============================================
  // 车辆操作
  // ============================================
  function initVehicleActions() {
    // 新增车辆
    const newVehicleBtn = document.getElementById('newVehicleBtn');
    if (newVehicleBtn) {
      newVehicleBtn.addEventListener('click', function() {
        window.location.href = './新增车辆.html';
      });
    }

    // 车辆详情
    document.querySelectorAll('.view-vehicle').forEach(btn => {
      btn.addEventListener('click', function(e) {
        e.stopPropagation();
        const vehicleId = this.dataset.vehicleId;
        window.location.href = './车辆管理详情.html?id=' + vehicleId;
      });
    });

    // 编辑车辆
    document.querySelectorAll('.edit-vehicle').forEach(btn => {
      btn.addEventListener('click', function(e) {
        e.stopPropagation();
        const vehicleId = this.dataset.vehicleId;
        window.location.href = './编辑车辆.html?id=' + vehicleId;
      });
    });

    // 删除车辆
    document.querySelectorAll('.delete-vehicle').forEach(btn => {
      btn.addEventListener('click', function(e) {
        e.stopPropagation();
        const vehicleId = this.dataset.vehicleId;
        if (confirm('确定要删除该车辆吗？')) {
          showToast('车辆删除成功', 'success');
          setTimeout(() => {
            window.location.reload();
          }, 1000);
        }
      });
    });

    // 提交新增车辆
    const submitVehicleBtn = document.getElementById('submitVehicleBtn');
    if (submitVehicleBtn) {
      submitVehicleBtn.addEventListener('click', function() {
        const form = document.getElementById('vehicleForm');
        if (validateRequired(form)) {
          submitWithLoading(this, function() {
            showToast('车辆新增成功', 'success');
            setTimeout(() => {
              window.location.href = './车辆管理.html';
            }, 1500);
          });
        }
      });
    }
  }

  // ============================================
  // 司机操作
  // ============================================
  function initDriverActions() {
    // 新增司机
    const newDriverBtn = document.getElementById('newDriverBtn');
    if (newDriverBtn) {
      newDriverBtn.addEventListener('click', function() {
        window.location.href = './新增司机.html';
      });
    }

    // 司机详情
    document.querySelectorAll('.view-driver').forEach(btn => {
      btn.addEventListener('click', function(e) {
        e.stopPropagation();
        const driverId = this.dataset.driverId;
        window.location.href = './司机管理详情.html?id=' + driverId;
      });
    });

    // 编辑司机
    document.querySelectorAll('.edit-driver').forEach(btn => {
      btn.addEventListener('click', function(e) {
        e.stopPropagation();
        const driverId = this.dataset.driverId;
        window.location.href = './编辑司机.html?id=' + driverId;
      });
    });

    // 删除司机
    document.querySelectorAll('.delete-driver').forEach(btn => {
      btn.addEventListener('click', function(e) {
        e.stopPropagation();
        const driverId = this.dataset.driverId;
        if (confirm('确定要删除该司机吗？')) {
          showToast('司机删除成功', 'success');
          setTimeout(() => {
            window.location.reload();
          }, 1000);
        }
      });
    });

    // 提交新增司机
    const submitDriverBtn = document.getElementById('submitDriverBtn');
    if (submitDriverBtn) {
      submitDriverBtn.addEventListener('click', function() {
        const form = document.getElementById('driverForm');
        if (validateRequired(form)) {
          submitWithLoading(this, function() {
            showToast('司机新增成功', 'success');
            setTimeout(() => {
              window.location.href = './司机管理.html';
            }, 1500);
          });
        }
      });
    }

    // 切换司机状态
    document.querySelectorAll('.toggle-driver-status').forEach(btn => {
      btn.addEventListener('click', function() {
        const driverId = this.dataset.driverId;
        const newStatus = this.dataset.status;
        showToast('状态已更新为: ' + getStatusText(newStatus), 'success');
      });
    });
  }

  function getStatusText(status) {
    const statusMap = {
      'idle': '空闲',
      'transporting': '运输中',
      'onLeave': '请假'
    };
    return statusMap[status] || status;
  }

  // ============================================
  // 智能调度操作
  // ============================================
  function initDispatchActions() {
    // 选中订单
    document.querySelectorAll('.dispatch-order-checkbox').forEach(checkbox => {
      checkbox.addEventListener('change', function() {
        updateSelectedOrders();
      });
    });

    // 智能派单
    const smartDispatchBtn = document.getElementById('smartDispatchActionBtn');
    if (smartDispatchBtn) {
      smartDispatchBtn.addEventListener('click', function() {
        const checked = document.querySelectorAll('.dispatch-order-checkbox:checked');
        if (checked.length === 0) {
          showToast('请选择要派单的订单', 'warning');
          return;
        }
        openModal('smartDispatchResultModal');
      });
    }

    // 手动派单
    const manualDispatchActionBtn = document.getElementById('manualDispatchActionBtn');
    if (manualDispatchActionBtn) {
      manualDispatchActionBtn.addEventListener('click', function() {
        const checked = document.querySelectorAll('.dispatch-order-checkbox:checked');
        if (checked.length === 0) {
          showToast('请选择要派单的订单', 'warning');
          return;
        }
        openModal('manualDispatchSelectModal');
      });
    }

    // 确认智能派单
    const confirmSmartResult = document.getElementById('confirmSmartResult');
    if (confirmSmartResult) {
      confirmSmartResult.addEventListener('click', function() {
        submitWithLoading(this, function() {
          closeModal('smartDispatchResultModal');
          showToast('智能派单成功', 'success');
          setTimeout(() => {
            window.location.reload();
          }, 1500);
        });
      });
    }

    // 确认手动派单
    const confirmManualSelect = document.getElementById('confirmManualSelect');
    if (confirmManualSelect) {
      confirmManualSelect.addEventListener('click', function() {
        const vehicle = document.getElementById('dispatchVehicleSelect');
        const driver = document.getElementById('dispatchDriverSelect');

        if (!vehicle.value || !driver.value) {
          showToast('请选择车辆和司机', 'warning');
          return false;
        }

        submitWithLoading(this, function() {
          closeModal('manualDispatchSelectModal');
          showToast('手动派单成功', 'success');
          setTimeout(() => {
            window.location.reload();
          }, 1500);
        });
      });
    }

    // 选择车辆
    document.querySelectorAll('.select-vehicle-btn').forEach(btn => {
      btn.addEventListener('click', function() {
        const vehicleNo = this.dataset.vehicleNo;
        const select = document.getElementById('dispatchVehicleSelect');
        if (select) {
          select.value = vehicleNo;
          showToast('已选择车辆: ' + vehicleNo, 'info');
        }
      });
    });

    // 选择司机
    document.querySelectorAll('.select-driver-btn').forEach(btn => {
      btn.addEventListener('click', function() {
        const driverName = this.dataset.driverName;
        const select = document.getElementById('dispatchDriverSelect');
        if (select) {
          select.value = driverName;
          showToast('已选择司机: ' + driverName, 'info');
        }
      });
    });
  }

  function updateSelectedOrders() {
    const checked = document.querySelectorAll('.dispatch-order-checkbox:checked');
    const count = checked.length;
    const actionArea = document.querySelector('.dispatch-action-area');

    if (actionArea) {
      const countEl = actionArea.querySelector('.selected-count');
      if (countEl) {
        countEl.textContent = count;
      }
      actionArea.style.display = count > 0 ? 'block' : 'none';
    }
  }

  // ============================================
  // 运输轨迹操作
  // ============================================
  function initTrackActions() {
    // 任务列表选中
    document.querySelectorAll('.track-task-item').forEach(item => {
      item.addEventListener('click', function() {
        document.querySelectorAll('.track-task-item').forEach(i => i.classList.remove('active'));
        this.classList.add('active');

        const taskId = this.dataset.taskId;
        showTaskDetail(taskId);
      });
    });

    // 轨迹回放
    const replayBtn = document.getElementById('trackReplayBtn');
    if (replayBtn) {
      replayBtn.addEventListener('click', function() {
        showToast('轨迹回放功能启动中...', 'info');
        // 模拟回放动画
        let progress = 0;
        const progressBar = document.getElementById('replayProgress');
        const interval = setInterval(() => {
          progress += 5;
          if (progressBar) progressBar.style.width = progress + '%';
          if (progress >= 100) {
            clearInterval(interval);
            showToast('回放完成', 'success');
          }
        }, 200);
      });
    }

    // 更新运输状态
    const updateStatusBtns = document.querySelectorAll('.update-track-status');
    updateStatusBtns.forEach(btn => {
      btn.addEventListener('click', function() {
        const newStatus = this.dataset.status;
        if (confirm('确认更新状态为: ' + newStatus + ' ?')) {
          showToast('状态更新成功', 'success');
          setTimeout(() => {
            window.location.reload();
          }, 1000);
        }
      });
    });

    // 筛选运输中
    const filterTransportingBtn = document.getElementById('filterTransporting');
    if (filterTransportingBtn) {
      filterTransportingBtn.addEventListener('click', function() {
        document.querySelectorAll('.track-task-item').forEach(item => {
          const status = item.dataset.status;
          item.style.display = status === 'transporting' ? '' : 'none';
        });
        showToast('已筛选运输中任务', 'success');
      });
    }
  }

  function showTaskDetail(taskId) {
    const detailPanel = document.getElementById('trackDetailPanel');
    if (detailPanel) {
      detailPanel.classList.add('show');
      showToast('加载任务详情...', 'info');
    }
  }

  // ============================================
  // 异常处理操作
  // ============================================
  function initExceptionActions() {
    // 登记异常
    const registerExceptionBtn = document.getElementById('registerExceptionBtn');
    if (registerExceptionBtn) {
      registerExceptionBtn.addEventListener('click', function() {
        openModal('registerExceptionModal');
      });
    }

    // 确认登记异常
    const confirmRegisterException = document.getElementById('confirmRegisterException');
    if (confirmRegisterException) {
      confirmRegisterException.addEventListener('click', function() {
        const form = document.getElementById('exceptionForm');
        if (validateRequired(form)) {
          submitWithLoading(this, function() {
            closeModal('registerExceptionModal');
            showToast('异常登记成功', 'success');
          });
        }
      });
    }

    // 异常详情
    document.querySelectorAll('.view-exception').forEach(btn => {
      btn.addEventListener('click', function(e) {
        e.stopPropagation();
        const exceptionId = this.dataset.exceptionId;
        window.location.href = './异常详情.html?id=' + exceptionId;
      });
    });

    // 处理异常
    document.querySelectorAll('.handle-exception').forEach(btn => {
      btn.addEventListener('click', function(e) {
        e.stopPropagation();
        const exceptionId = this.dataset.exceptionId;
        openModal('handleExceptionModal' + exceptionId);
      });
    });

    // 确认处理异常
    document.querySelectorAll('.confirmHandleException').forEach(btn => {
      btn.addEventListener('click', function() {
        const exceptionId = this.dataset.exceptionId;
        submitWithLoading(this, function() {
          closeModal('handleExceptionModal' + exceptionId);
          showToast('异常处理成功', 'success');
          setTimeout(() => {
            window.location.reload();
          }, 1500);
        });
      });
    });

    // 异常筛选
    const exceptionStatusFilter = document.getElementById('exceptionStatusFilter');
    if (exceptionStatusFilter) {
      exceptionStatusFilter.addEventListener('change', function() {
        const status = this.value;
        document.querySelectorAll('.exception-row').forEach(row => {
          const rowStatus = row.dataset.status;
          row.style.display = (status === 'all' || rowStatus === status) ? '' : 'none';
        });
        showToast('筛选完成', 'success');
      });
    }
  }

  // ============================================
  // 首页操作
  // ============================================
  function initHomeActions() {
    // 快捷操作
    document.querySelectorAll('.quick-action').forEach(btn => {
      btn.addEventListener('click', function() {
        const route = this.dataset.route;
        if (route) {
          window.location.href = route;
        }
      });
    });

    // 待办事项点击
    document.querySelectorAll('.todo-item').forEach(item => {
      item.addEventListener('click', function() {
        const route = this.dataset.route;
        const status = this.dataset.status;
        if (route) {
          if (status) {
            window.location.href = route + '?status=' + status;
          } else {
            window.location.href = route;
          }
        }
      });
    });

    // 指标卡片点击
    document.querySelectorAll('.metric-card').forEach(card => {
      card.addEventListener('click', function() {
        const route = this.dataset.route;
        if (route) {
          window.location.href = route;
        }
      });
    });

    // 时间切换
    const timeRangeBtns = document.querySelectorAll('.time-range-btn');
    timeRangeBtns.forEach(btn => {
      btn.addEventListener('click', function() {
        timeRangeBtns.forEach(b => b.classList.remove('active'));
        this.classList.add('active');
        showToast('切换时间范围: ' + this.textContent, 'info');
      });
    });
  }

  // ============================================
  // 数据导出
  // ============================================
  function initDataExport() {
    document.querySelectorAll('.export-btn').forEach(btn => {
      btn.addEventListener('click', function() {
        const type = this.dataset.exportType || 'data';
        showToast('正在导出' + type + '...', 'info');

        setTimeout(() => {
          showToast(type + '导出成功', 'success');
        }, 1500);
      });
    });
  }

  // ============================================
  // 用户菜单
  // ============================================
  function initUserMenu() {
    const userAvatar = document.querySelector('.user-avatar');
    const userMenu = document.querySelector('.user-menu');

    if (userAvatar && userMenu) {
      userAvatar.addEventListener('click', function(e) {
        e.stopPropagation();
        userMenu.classList.toggle('show');
      });

      document.addEventListener('click', function() {
        userMenu.classList.remove('show');
      });
    }

    // 退出登录
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
      logoutBtn.addEventListener('click', function() {
        if (confirm('确定要退出登录吗？')) {
          showToast('退出成功', 'success');
          setTimeout(() => {
            window.location.href = './index.html';
          }, 1000);
        }
      });
    }
  }

  // ============================================
  // URL 参数读取工具
  // ============================================
  window.getUrlParam = function(name) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(name);
  };

  // 初始化时读取 URL 参数
  window.addEventListener('DOMContentLoaded', function() {
    const orderId = getUrlParam('orderId');
    const status = getUrlParam('status');
    const id = getUrlParam('id');

    // 如果有订单 ID，自动选中
    if (orderId) {
      const checkbox = document.querySelector('.dispatch-order-checkbox[data-order-id="' + orderId + '"]');
      if (checkbox) {
        checkbox.checked = true;
        updateSelectedOrders();
      }
    }

    // 如果有状态筛选，自动应用
    if (status) {
      const statusFilter = document.getElementById('orderStatusFilter') ||
                          document.getElementById('exceptionStatusFilter') ||
                          document.getElementById('vehicleStatusFilter') ||
                          document.getElementById('driverStatusFilter');
      if (statusFilter) {
        statusFilter.value = status;
        statusFilter.dispatchEvent(new Event('change'));
      }
    }
  });

  // ============================================
  // 角色切换（仅用于演示）
  // ============================================
  window.switchRole = function(role) {
    AppState.currentRole = role;
    showToast('已切换角色: ' + getRoleName(role), 'info');
    setTimeout(() => {
      window.location.reload();
    }, 500);
  };

  function getRoleName(role) {
    const roleMap = {
      'admin': '超级管理员',
      'manager': '物流经理',
      'dispatcher': '调度员',
      'service': '客服人员',
      'warehouse': '仓库管理员',
      'driver': '司机',
      'finance': '财务人员'
    };
    return roleMap[role] || role;
  }

})();