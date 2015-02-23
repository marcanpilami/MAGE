#!/bin/bash

function mage_query
{
    typeset query s arg ok tmpHeaders http_code
    OPTIND=1
    while getopts "q:s:" arg
    do
        case ${arg} in
            q) # query
                query="$OPTARG"
                ;;
            s) # session id
                s="$OPTARG"
                ;;
            *)
                return 1
                ;;
        esac
    done

    ## Checks
    if [[ ! -r $s ]]
    then
        echo "session does not exist" >&2
        return 1
    fi

    tmpHeaders=/tmp/t1_$$_$RANDOM
    rm -f $tmpHeaders >/dev/null 2>&1

    wget -q -S --load-cookies=$s -O - "${MAGE_BASE_URL}/${query}" 2>${tmpHeaders}
    ok=$?

    http_code=$(($(grep "HTTP/1" ${tmpHeaders} | cut -d' ' -f4)))
    rm -f $tmpHeaders >/dev/null 2>&1
    if [[ $http_code -ne 200 ]] || [[ $ok -ne 0 ]]
    then
        echo "query did not complete correctly (code 200). HTTP code will be returned on stdout. HTTP code $http_code - WGET code $ok - Query was ${MAGE_BASE_URL}/$query" >&2		
        echo ${http_code}
        return 1
    fi

    return 0
}

function mage_login
{
    typeset tmpFile session_id

    if [[ "${MAGE_USER}" == "" ]] || [[ ${MAGE_PASSWORD} == "" ]] ||  [[ ${MAGE_BASE_URL} == "" ]] 
    then
        if [[ $# -eq 3 ]]
        then
            export MAGE_BASE_URL="$1"
            export MAGE_USER="$2"
            export MAGE_PASSWORD="$3"
        else
            printf "MAGE_USER and MAGE_PASSWORD are not specified - either as arguments or as environment variables" >&2
            return 1
        fi	
    fi

    session_id="/tmp/cookie_$$_$RANDOM"
    res=$(wget -q -S --keep-session-cookies --save-cookies=${session_id} --post-data="username=${MAGE_USER}&password=${MAGE_PASSWORD}" ${MAGE_BASE_URL}{% url 'script_login_post' %} 2>&1)
    ok=$?
    if [[ $ok -ne 0 ]]
    then
        if [[ "$res" == "401" ]]
        then
            echo "ERROR wrong MAGE login/password" >&2
        else
            echo "ERROR generic error in MAGE connection" >&2
        fi
        return $ok
    fi
    
    echo ${session_id}
}

function mage_logout
{
    typeset arg ss

    OPTIND=1
    while getopts "s:" arg
    do
        case $arg in
            s) # sessionid
                ss="$OPTARG"
                ;;		
        esac
    done
    if [[ ! -r $ss ]]
    then
        echo "WARNING session does not exist so it won't be closed" >&2
        return 1
    fi

    mage_query -q "accounts/scriptlogout" -s $ss >/dev/null
    ok=$?
    if [[ $ok -ne 0 ]]
    then
        echo "WARNING error in MAGE logout" >&2		
    fi
    rm -f $s
    return 0
}

function mage_run_query
{
    typeset s tmpFile arg ok query u
    u=0
    OPTIND=1
    while getopts "q:s:u?" arg
    do
        case $arg in
            q) # query
                query="$OPTARG"
                ;;
            s) # session token
                s="$OPTARG"
                ;;
            u) # unique result
                u=1;
                ;;
            *)
                return 1
                ;;
        esac
    done

    tmpFile="/tmp/tmpQuery_$$_$RANDOM"
    mage_query -q "ref/mql/sh/${query}" -s $s >$tmpFile
    ok=$?

    if [[ $ok -ne 0 ]]
    then
        cat $tmpFile >&2
        rm -f $tmpFile
        return $ok
    fi

    . $tmpFile
    rm -f $tmpFile  

    if [[ ${MAGE_RESULT_COUNT} -eq 0 ]] && [[ $u -eq 1 ]]
    then    
        echo "ERROR query awaited a single result but there were none returned" >&2
        return 3
    elif [[ ${MAGE_RESULT_COUNT} -gt 1 ]] && [[ $u -eq 1 ]]
    then
        echo "ERROR query awaited a single result but there were more" >&2
        return 4
    fi

    return $ok
}

function mage_get_result
{
    typeset i l a f o arg
    i=1
    l=0
    OPTIND=1    
    while getopts "i:a:l?q:" arg
    do
        case $arg in
            i) # index. Ignored if -l. Default is 1 (the first index).
                i="$OPTARG"
                ;;
            a) # attribute name requested
                a="$OPTARG"
                ;;
            l) # list of results (one result per line) instead of single result.
                l=1
                ;;
            *)
                return 1
                ;;
        esac
    done
    if [[ "$a" == "" ]]
    then
        echo "ERROR an argument name must be given" >&2
        return 1
    fi
    a=$(echo $a | tr "[a-z]" "[A-Z]")

    if [[ $l -eq 0 ]]
    then
        for f in $(eval "echo \$MAGE_${i}_MAGE_FIELDS")
        do
            if [[ $f == $a ]]
            then
                break
            fi
        done
        if [[ $f != $a ]]
        then    
            echo "ERROR result $i has no field named $a" >&2
            return 1
        fi
        
        eval "echo \$MAGE_${i}_${a}"
    else
        o=0
        while [[ $o -le ${MAGE_RESULT_COUNT} ]]
        do
            eval "echo \"\$MAGE_${o}_${a}\""
            o=$(($o+1))
        done
    fi
}

function mage_get_delivery_id
{
    typeset s delivery arg ok
    OPTIND=1

    while getopts "d:s:" arg
    do
        case $arg in
            s) # session token
                s="$OPTARG"
                ;;
            d) # delivery name
                delivery=$OPTARG
                ;;
            *)
                return 1
                ;;
        esac
    done
    if [[ "${delivery}" == "" ]]
    then
        echo "ERROR delivery name must be specified" >&2
        return 1
    fi

    mage_query -q "scm/is/${delivery}/id" -s $s
    return $?
}

function mage_get_delivery_content
{
    typeset del arg tmpFile ok
    OPTIND=1
    while getopts "s:i:" arg
    do
        case $arg in
            s) # session token
                s="$OPTARG"
                ;;
            i) # set ID
                del=$OPTARG
                ;;
            *)
                return 1
                ;;
        esac
    done

    tmpFile="/tmp/tmpQuery_$$_$RANDOM"
    mage_query -q "scm/is/${del}/export/sh" -s $s > $tmpFile
    ok=$?
    if [[ $ok -ne 0 ]]
    then
        echo "Could not retrieve delivery content for delivery ${del}" >&2
        return $ok
    fi

    . $tmpFile
    rm -f $tmpFile
    return 0
}

function mage_get_install_methods
{   
    # also for testing compatibility: if no install method, not compatible.
    typeset ii ci s arg
    OPTIND=1
    while getopts "s:i:c:" arg
    do
        case $arg in
            s) # session token
                s="$OPTARG"
                ;;
            i) # installableitem ID
                ii=$OPTARG
                ;;
            c) # component instance ID
                ci=$OPTARG
                ;;
            *)
                return 1
                ;;
        esac
    done

    mage_query -q "scm/ii/${ii}/installmethod/${ci}" -s $s
    return $?
}

function mage_get_compatible_installable_items
{   
    # also for testing compatibility: if no II returned, not compatible.
    typeset s is ci arg
    OPTIND=1
    while getopts "s:i:c:" arg
    do
        case $arg in
            s) # session token
                s="$OPTARG"
                ;;
            i) # installable set ID (or name)
                is="$OPTARG"
                ;;
            c) # component instance ID
                ci=$OPTARG
                ;;
            *)
                return 1
                ;;
        esac
    done

    mage_query -q "scm/is/${is}/ii/iicompatlist/${ci}" -s $s
    return $?
}

function mage_test_ii_dependencies
{
    typeset arg ii s e ok res full
	OPTIND=1
    full=0
	while getopts "s:i:e:f?" arg
	do
		case $arg in
            s) # session token
                s="$OPTARG"
                ;;
			i) # installableitem ID
				ii=$OPTARG
				;;
            e) # environment name
                e=$OPTARG
                ;;
            f) # if set, consider the install of the set as a whole in the version dependencies checks
                full=1
                ;;
			*)
				return 1
				;;
		esac
	done
    
    if [[ $full -eq 1 ]]
    then
        res=$(mage_query -s $s -q "scm/ii/$ii/testonenvtscriptfull/$e")
    else
        res=$(mage_query -s $s -q "scm/ii/$ii/testonenvtscriptsingle/$e")
    fi
	# note that only very recent wget have --content-on-error option. So this will not display the failed dependency.
    return $?
}

function mage_helper_test_before_install
{
    # Helper method, which makes a few assumptions:
    #   * only one CI is modified (the method can however be called as many times as needed)
    #   * the installable set only contains one item which is compatible with the component instance.
    #   * the CI belongs to one and only one environment
    
    typeset s q d del_id ci_id iis nb e ci_envt ii_id
    OPTIND=1
    while getopts "s:d:q:e:" arg
    do
        case $arg in
            s) # session token
                s="$OPTARG"
                ;;
            q) # query to identify the Component Instance (CI) that the package will be applied to
                q="$OPTARG"
                ;;
            d) # name of the delivery
                d="$OPTARG"
                ;;
            *) 
                return 1
                ;;
        esac
    done

    # check delivery exists
    del_id=$(mage_get_delivery_id -s $s -d $d)
    if [[ $? -ne 0 ]]
    then
        echo "error: delivery could not be found in the repository (name [$d])"
        return 11
    fi    
    
    # check the CI exists
    mage_run_query -s $s -q "$q" -u
    if [[ $? -ne 0 ]]
    then
        echo "component instance could not be found in the repository with query [$q]"
        return 12
    fi
    ci_id=$(mage_get_result -a mage_id)
    ci_envt=$(mage_get_result -a MAGE_ENVIRONMENTS)
    
    # Check the CI is of a logical type contained in the delivery
    iis=$(mage_get_compatible_installable_items -s $s -c ${ci_id} -i ${del_id})
    if [[ $? -ne 0 ]]
    then
        echo "could not retrieve compatible items inside delivery"
        return 13
    fi
    nb=$(($(echo "$iis" | wc -l)))
    if [[ $nb -eq 0 ]]
    then
        echo "Error: there are no compatible items inside this delivery"
        return 14
    fi
    if [[ $nb -gt 1 ]]
    then    
        echo "Error: there are more than one items which are compatible with the component instance. This helper method cannot choose by itself - use more granular API method instead"
        return 15
    fi
    
    # Check version...
    mage_test_ii_dependencies -s $s -i ${iis} -e ${ci_envt} 2>/dev/null
    if [[ $? -ne 0 ]]
    then
        echo "ERROR the component is not in a version compatible with this delivery"
        return 16
    fi
    
    ## If here, everything exist and there is one compatible (in type and version) II inside the delivery => can proceeed
    return 0
}

function mage_register_install
{
	typeset ii_id envt_name instance_id s arg ok
	OPTIND=1
	while getopts "s:i:e:t:" arg
	do
		case $arg in
            s) # session token
                s="$OPTARG"
                ;;
			i) # INSTALLABLE ITEM ID
				ii_id=$OPTARG
				;;
			e) # ENVT NAME
				envt_name=$OPTARG
				;;
			t) # TARGET INSTANCE ID
				instance_id=$OPTARG
				;;
			*)
				return 1
				;;
		esac
	done

	mage_query -q "scm/ii/${ii_id}/apply/${envt_name}/${instance_id}" -s $s
	return $?
}

function mage_helper_register_standard_install
{
    # Helper method, which makes the same assumptions as mage_helper_test_before_install
    
    typeset s q d del_id ci_id ci_envt iis nb e ii_id
    OPTIND=1
    while getopts "s:d:q:" arg
    do
        case $arg in
            s) # session token
                s="$OPTARG"
                ;;
            q) # query to identify the Component Instance (CI) that the package will be applied to
                q="$OPTARG"
                ;;
            d) # name of the delivery
                d="$OPTARG"
                ;;
            *) 
                return 1
                ;;
        esac
    done
    
    ## Checks (once again, it may not have been called before the install)
    mage_helper_test_before_install -s $s -q "$q" -d "$d"
    if [[ $? -ne 0 ]]
    then
        return 99
    fi
    
    ci_id=$(mage_get_result -a mage_id)
    ci_envt=$(mage_get_result -a MAGE_ENVIRONMENTS)
    ii_id=$(mage_get_compatible_installable_items -s $s -c ${ci_id} -i ${d})
    
    mage_register_install -s $s -i ${ii_id}  -e ${ci_envt} -t ${ci_id}
    if [[ $? -ne 0 ]]
    then    
        echo "ERROR could not register install"
        return 100
    fi
}


## TODO BELOW THIS POINT
function mage_get_file
{
	typeset iifile
	OPTIND=1
	while getopts "u:" arg
	do
		case $arg in
			u) # URL
				iifile=$(echo $OPTARG | sed "s|^/mage/||p")
				;;
			*)
				return 1
				;;
		esac
	done
	
	mage_query -q $iifile -s $$
	return $?
}


function mage_register_backup_ci
{
	typeset instance_id envt_name arg ok
	OPTIND=1
	while getopts "i:e:" arg
	do
		case $arg in
			i) # COMPONENT INSTANCE ID
				instance_id=$OPTARG
				;;
			e) # ENVT NAME
				envt_name=$OPTARG
				;;
			*)
				return 1
				;;
		esac
	done

	mage_query -q "scm/bck/create/envtscript/${envt_name}/${instance_id}" -s $$
	return $?
}

function mage_archive_backupset
{
	typeset bid arg ok
	OPTIND=1
	while getopts "i:" arg
	do
		case $arg in
			i) # BACKUP SET ID
				bid="$OPTARG"
				;;
			*)
				return 1
				;;
		esac
	done

	mage_query -q "scm/bck/${bid}/archive" -s $$	
	return $?
}

function mage_latest_backup_age
{
	typeset cid arg ok
	OPTIND=1
	while getopts "i:" arg
	do
		case $arg in
			i) # COMPONENT INSTANCE ID
				cid="$OPTARG"
				;;
			*)
				return 1
				;;
		esac
	done

	mage_query -q "scm/bck/api/ci/${cid}/latest" -s $$
	return $?
}


###############################################################################
## Samples
# export MAGE_BASE_URL="http://192.168.56.1:8000"
# s=$(mage_login ${MAGE_BASE_URL} a a)

# mage_run_query -s $s -q "SELECT 'jbossas' INSTANCES"
# mage_get_result -a name -l

# del_id=$(mage_get_delivery_id -s $s -d "Sprint_115")
# mage_get_delivery_content -s $s -i ${del_id}

# Is the delivery appliable to the component?
# mage_helper_test_before_install -s $s -q "SELECT ENVIRONMENT 'QUA1' OFFER 'padua_jqm_batch' 'jqmbatch' INSTANCES" -d "Sprint_115"

# Apply it (also checks as above)
# mage_helper_register_standard_install -s $s -q "SELECT ENVIRONMENT 'QUA1' OFFER 'padua_jqm_batch' 'jqmbatch' INSTANCES" -d "Sprint_115"