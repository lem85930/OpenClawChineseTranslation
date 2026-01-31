# ============================================================
# docker-deploy.ps1 测试
# 使用 Pester (PowerShell 测试框架)
# 兼容 Pester 3.x 和 5.x
# ============================================================

$ScriptPath = Join-Path (Split-Path (Split-Path $PSScriptRoot -Parent) -Parent) "docker-deploy.ps1"

# ============================================================
# 语法测试
# ============================================================

Describe "docker-deploy.ps1 语法验证" {
    It "脚本语法正确" {
        $errors = $null
        $null = [System.Management.Automation.PSParser]::Tokenize(
            (Get-Content $ScriptPath -Raw),
            [ref]$errors
        )
        $errors.Count | Should Be 0
    }
    
    It "脚本可以加载" {
        { . $ScriptPath -Help } | Should Not Throw
    }
}

# ============================================================
# 帮助信息测试
# ============================================================

Describe "帮助信息" {
    It "-Help 正常退出不抛出错误" {
        # Write-Host 输出不能被捕获，只验证正常退出
        { & $ScriptPath -Help } | Should Not Throw
    }
}

# ============================================================
# 参数解析测试
# ============================================================

Describe "参数解析" {
    It "接受 -Token 参数" {
        $scriptContent = Get-Content $ScriptPath -Raw
        $scriptContent | Should Match '\$Token'
    }
    
    It "接受 -Port 参数" {
        $scriptContent = Get-Content $ScriptPath -Raw
        $scriptContent | Should Match '\$Port'
    }
    
    It "接受 -Name 参数" {
        $scriptContent = Get-Content $ScriptPath -Raw
        $scriptContent | Should Match '\$Name'
    }
    
    It "接受 -LocalOnly 参数" {
        $scriptContent = Get-Content $ScriptPath -Raw
        $scriptContent | Should Match 'LocalOnly'
    }
    
    It "接受 -SkipInit 参数" {
        $scriptContent = Get-Content $ScriptPath -Raw
        $scriptContent | Should Match 'SkipInit'
    }
    
    It "接受 -Help 参数" {
        $scriptContent = Get-Content $ScriptPath -Raw
        $scriptContent | Should Match '\$Help'
    }
}

# ============================================================
# 脚本结构测试
# ============================================================

Describe "脚本结构" {
    It "脚本包含 Show-Banner 函数" {
        $scriptContent = Get-Content $ScriptPath -Raw
        $scriptContent | Should Match "function Show-Banner"
    }
    
    It "脚本包含 Test-Docker 函数" {
        $scriptContent = Get-Content $ScriptPath -Raw
        $scriptContent | Should Match "function Test-Docker"
    }
}

# ============================================================
# 配置测试
# ============================================================

Describe "脚本配置" {
    It "脚本设置 ErrorActionPreference" {
        $scriptContent = Get-Content $ScriptPath -Raw
        $scriptContent | Should Match 'ErrorActionPreference.*Stop'
    }
    
    It "脚本定义默认端口" {
        $scriptContent = Get-Content $ScriptPath -Raw
        $scriptContent | Should Match '18789'
    }
    
    It "脚本定义默认容器名" {
        $scriptContent = Get-Content $ScriptPath -Raw
        $scriptContent | Should Match 'openclaw'
    }
    
    It "脚本使用正确的镜像地址" {
        $scriptContent = Get-Content $ScriptPath -Raw
        $scriptContent | Should Match 'ghcr.io/1186258278/openclaw-zh'
    }
    
    It "脚本使用 nightly 标签" {
        $scriptContent = Get-Content $ScriptPath -Raw
        $scriptContent | Should Match 'nightly'
    }
}

# ============================================================
# 安全测试
# ============================================================

Describe "安全性检查" {
    It "脚本不包含硬编码的密码" {
        $scriptContent = Get-Content $ScriptPath -Raw
        $scriptContent | Should Not Match 'password\s*=\s*[''"][^''\"]{10,}[''"]'
    }
    
    It "Token 参数有默认空值" {
        $scriptContent = Get-Content $ScriptPath -Raw
        $scriptContent | Should Match '\$Token\s*=\s*""'
    }
}

# ============================================================
# Docker 配置测试
# ============================================================

Describe "Docker 配置" {
    It "脚本定义卷名变量" {
        $scriptContent = Get-Content $ScriptPath -Raw
        $scriptContent | Should Match 'VolumeName'
    }
    
    It "脚本定义镜像变量" {
        $scriptContent = Get-Content $ScriptPath -Raw
        $scriptContent | Should Match 'Image'
    }
}
