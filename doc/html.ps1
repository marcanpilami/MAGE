if (! (Test-Path $PSScriptRoot/html ))
{
    mkdir $PSScriptRoot/html
}
& sphinx-build.exe -a -b html $PSScriptRoot $PSScriptRoot/html
