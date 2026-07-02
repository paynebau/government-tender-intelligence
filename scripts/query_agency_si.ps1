param(
    [Parameter(Mandatory = $true)]
    [string]$Agency,
    [int]$StartYear = 2021,
    [int]$EndYear = 2025,
    [string]$DataDir = "",
    [string]$Output = ""
)

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
if (-not $DataDir) {
    $DataDir = Get-ChildItem -LiteralPath $ProjectRoot -Directory |
        Where-Object { $_.Name -like "*_CSV" } |
        Select-Object -First 1 -ExpandProperty FullName
}
if (-not $Output) {
    $Output = Join-Path $ProjectRoot "output\agency_report_2021_2025.csv"
}

$records = New-Object System.Collections.Generic.List[object]

Get-ChildItem -LiteralPath $DataDir -Filter "*SourceData.csv" | Sort-Object Name | ForEach-Object {
    if ($_.Name -notmatch "award_(\d{4})") {
        return
    }

    $year = [int]$Matches[1]
    if ($year -lt $StartYear -or $year -gt $EndYear) {
        return
    }

    $sourceCsv = $_.Name
    Import-Csv -LiteralPath $_.FullName | Where-Object {
        ($_.TenderOrgName).Trim() -eq $Agency
    } | ForEach-Object {
        $amountText = [string]$_.TenderAwardPrice
        $amountDigits = $amountText -replace "[^\d]", ""
        $amount = if ($amountDigits) { [int64]$amountDigits } else { 0 }

        $records.Add([pscustomobject]@{
            '年度' = $year
            '機關' = $_.TenderOrgName
            '標案名稱' = $_.TenderName
            '金額' = $amount
            '得標廠商' = $_.BidderSuppName
            '協作廠商' = $_.NotObtainSuppName
            '標案案號' = $_.TenderCaseNo
            '決標日期' = $_.AwardDate
            '採購類型' = $_.ProcurementType
            '採購屬性' = $_.ProcurementAttr
            '決標方式' = $_.TenderAwardWay
            '原始來源' = $_.SourceFile
            'CSV 來源' = $sourceCsv
        }) | Out-Null
    }
}

$sortedRecords = $records | Sort-Object '年度', '決標日期', '標案案號'
$outputDir = Split-Path -Parent $Output
New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
$sortedRecords | Export-Csv -LiteralPath $Output -NoTypeInformation -Encoding UTF8

$total = ($sortedRecords | Measure-Object -Property '金額' -Sum).Sum
Write-Output "records: $($sortedRecords.Count)"
Write-Output "total_amount: $total"
Write-Output "amount_by_supplier:"
$sortedRecords |
    Group-Object '得標廠商' |
    ForEach-Object {
        [pscustomobject]@{
'得標廠商' = $_.Name
'金額' = ($_.Group | Measure-Object -Property '金額' -Sum).Sum
        }
    } |
    Sort-Object '金額' -Descending |
    ForEach-Object {
        Write-Output "- $($_.'得標廠商'): $($_.'金額')"
    }
Write-Output "output: $Output"



