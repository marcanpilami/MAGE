#!/bin/bash

function mage_query
{
    typeset query s arg ok tmpHeaders http_code headers
    OPTIND=1
    while getopts "q:s:" arg
    do
        case ${arg} in
            q) # HTTP query. If relative, will be appended to $MAGE_BASE_URL
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
    if [[ "$s" == "" ]]
    then
        echo "ERROR: a session must be provided. Use mage_login to create a session object"
        return 1
    fi
    if [[ ! -r $s ]]
    then
        echo "session does not exist" >&2
        return 1
    fi
    
    ## Create absolute URL
    query=$(mage_url -q "${query}")

    ## Run command
    tmpHeaders=/tmp/t1_$$_$RANDOM
    rm -f $tmpHeaders >/dev/null 2>&1

    wget -q -S --load-cookies=$s -O - "${query}" 2>${tmpHeaders}
    ok=$?

    http_code=$(($(cat $tmpHeaders | grep -v "302" | grep "HTTP/1" | cut -d' ' -f4)))
    headers=(cat $tmpHeaders)
    rm -f $tmpHeaders >/dev/null 2>&1
    if [[ $http_code -ne 200 ]] || [[ $ok -ne 0 ]]
    then
        echo "ERROR query did not complete correctly. HTTP code $http_code - WGET code $ok - Query was $query" >&2
        echo ${http_code}
        return 1
    fi

    return 0
}

function mage_login
{
    typeset tmpFile tmpHeaders session_id query

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

    query=$(mage_url -q "accounts/scriptlogin")
    session_id="/tmp/cookie_$$_$RANDOM"
    tmpHeaders=/tmp/t1_$$_$RANDOM
    rm -f ${tmpHeaders} ${session_id} >/dev/null 2>&1
        
    wget -q -S --keep-session-cookies --save-cookies=${session_id} --load-cookies=$s --post-data="username=${MAGE_USER}&password=${MAGE_PASSWORD}" -O /dev/null "${query}" 2>${tmpHeaders}
    ok=$?
    http_code=$(($(cat $tmpHeaders | grep -v "302" | grep "HTTP/1" | cut -d' ' -f4)))
    headers=(cat $tmpHeaders)
    rm -f $tmpHeaders >/dev/null 2>&1
    if [[ $http_code -ne 200 ]] || [[ $ok -ne 0 ]]
    then
        if [[ "${http_code}" -eq "401" ]]
        then
            echo "ERROR wrong MAGE login/password" >&2
        else
            echo "ERROR login query did not complete correctly. HTTP code $http_code - WGET code $ok - Query was $query" >&2
        fi
    fi

    echo ${session_id}
    return $ok
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

function mage_run_csv_query
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
    mage_query -q "ref/mql/csv/${query}" -s $s | tail -n +2 >$tmpFile
    ok=$?

    if [[ $ok -ne 0 ]]
    then
        cat $tmpFile >&2
        rm -f $tmpFile
        return $ok
    fi
    
    result_count=$(cat $tmpFile | wc -l)

    if [[ ${result_count} -eq 0 ]] && [[ $u -eq 1 ]]
    then    
        echo "ERROR query awaited a single result but there were none returned" >&2
        return 3
    elif [[ ${result_count} -gt 1 ]] && [[ $u -eq 1 ]]
    then
        echo "ERROR query awaited a single result but there were more" >&2
        return 4
    fi
    
    cat $tmpFile
    rm -f $tmpFile  
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
        o=1
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
            d) # delivery name (or ID!)
                delivery="$OPTARG"
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
    # This is a test for being a numeral...
    printf "%d" $delivery >/dev/null 2>&1
    if [[ $? -eq 0 ]]
    then
        echo $delivery
        return 0
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

function mage_get_installable_item_detail
{
    typeset s ii arg tmpFile ok
    OPTIND=1
    while getopts "s:i:" arg
    do
        case $arg in
            s) # session token
                s="$OPTARG"
                ;;
            i) # item ID
                ii=$OPTARG
                ;;
            *)
                return 1
                ;;
        esac
    done

    tmpFile="/tmp/tmpQuery_$$_$RANDOM"
    mage_query -q "scm/ii/${ii}/export/sh" -s $s > $tmpFile
    ok=$?
    if [[ $ok -ne 0 ]]
    then
        echo "Could not retrieve description of installable item ${ii}" >&2
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
    
    typeset s q d del_id ci_id iis nb e ci_envt ii_id f
    OPTIND=1
    while getopts "s:d:q:e:f:?" arg
    do
        case $arg in
            s) # session token
                s="$OPTARG"
                ;;
            q) # query to identify the Component Instance (CI) that the package will be applied to
                q="$OPTARG"
                ;;
            d) # name or ID of the delivery.
                d="$OPTARG"
                ;;
            f) # path of the file to download - if not given, no download will take place
                f="$OPTARG"
                ;;
            *) 
                return 1
                ;;
        esac
    done
    
    if [[ "$q" == "" ]]
    then
        echo "ERROR: no query given" >&2
        return 1
    fi

    # check delivery exists if given by name
    del_id=$(mage_get_delivery_id -s $s -d "$d")
    if [[ $? -ne 0 ]]
    then
        echo "error: delivery could not be found in the repository (name [$d])" >&2
        return 11
    fi
    
    # check the CI exists
    mage_run_query -s $s -q "$q" -u
    if [[ $? -ne 0 ]]
    then
        echo "component instance could not be found in the repository with query [$q]" >&2
        return 12
    fi
    ci_id=$(mage_get_result -a mage_id)
    ci_envt=$(mage_get_result -a MAGE_ENVIRONMENTS)
    
    # Check the CI is of a logical type contained in the delivery
    iis=$(mage_get_compatible_installable_items -s $s -c ${ci_id} -i ${del_id})
    if [[ $? -ne 0 ]]
    then
        echo "Error: could not retrieve compatible items inside delivery" >&2
        return 13
    fi
    
    nb=$(($(echo "$iis" | wc -l)))
    if [[ $nb -eq 0 ]] || [[ "$iis" == "" ]]
    then
        echo "Error: there are no compatible items inside this delivery" >&2
        return 14
    fi
    if [[ $nb -gt 1 ]]
    then    
        echo "Error: there are more than one items which are compatible with the component instance. This helper method cannot choose by itself - use more granular API method instead" >&2
        return 15
    fi
    
    # Perhaps download the file
    if [[ "$f" != "" ]]
    then
        mage_get_installable_item_detail -s $s -i ${iis}
        if [[ $? -ne 0 ]]
        then
            return 18
        fi
        
        if [[ "${MAGE_IS_II_1_URL}" == "" ]]
        then
            echo "ERROR asked to download a file but there is no file associated to the delivery item" >&2
            return 19
        fi
        
        if [[ ! -w $(dirname $f) ]]
        then
            echo "ERROR no permissions to create file at $f" >&2
            return 20
        fi
        
        mage_get_file -s $s -u ${MAGE_IS_II_1_URL} >$f
    fi
    
    # Check version...
    mage_test_ii_dependencies -s $s -i ${iis} -e ${ci_envt} 2>/dev/null
    if [[ $? -ne 0 ]]
    then
        echo "ERROR the component is not in a version compatible with this delivery" >&2
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
            d) # name or ID of the delivery
                d="$OPTARG"
                ;;
            *) 
                return 1
                ;;
        esac
    done
    
    ## Checks (once again, it may not have been called before the install)
    mage_helper_test_before_install -s "$s" -q "$q" -d "$d"
    ok=$?
    ## 16 is OK - we consider a prerequisite failure is already accepted
    if [[ $ok -ne 0 ]] && [[ $ok -ne 16 ]]
    then
        return 99
    fi
    
    ci_id=$(mage_get_result -a mage_id)
    ci_envt=$(mage_get_result -a MAGE_ENVIRONMENTS)
    ii_id=$(mage_get_compatible_installable_items -s $s -c ${ci_id} -i ${d})
    
    mage_register_install -s $s -i ${ii_id}  -e ${ci_envt} -t ${ci_id}
    if [[ $? -ne 0 ]]
    then    
        echo "ERROR could not register install" >&2
        return 100
    fi
}

function mage_get_file
{
    typeset iifile s
    OPTIND=1
    while getopts "s:u:" arg
    do
        case $arg in
            s) # session token
                s="$OPTARG"
                ;;
            u) # URL. The full URL given by MAGE itself inside the II description
                iifile="$OPTARG"
                ;;
            *)
                return 1
                ;;
        esac
    done

    mage_query -s $s -q $iifile
    return $?
}

function mage_register_backup_ci
{
	typeset instance_id envt_name arg ok s q
	OPTIND=1
	while getopts "s:i:e:q:" arg
	do
		case $arg in
            s) # session token
                s="$OPTARG"
                ;;
			i) # COMPONENT INSTANCE ID
				instance_id=$OPTARG
				;;
			e) # ENVT NAME
				envt_name=$OPTARG
				;;
            q) # Query to find the component instance (ignored if -i is used)
                q="$OPTARG"
                ;;
			*)
				return 1
				;;
		esac
	done

    if [[ "${instance_id}" == "" ]] && [[ "$q" == "" ]]
    then
        echo "ERROR either give an instance id  with -i or a query to find the instance with -q" >&2
        return 1
    fi
    
    if [[ "${instance_id}" == "" ]] && [[ "$q" != "" ]]
    then
        mage_run_query -s $s -u -q "$q"
        if [[ $? -ne 0 ]]
        then
            return 1
        fi
        
        instance_id=$(mage_get_result -a mage_id)
    fi
    
	mage_query -s $s -q "scm/bck/create/script/${envt_name}/${instance_id}"
	return $?
}

function mage_archive_set
{
	typeset bid arg ok s
	OPTIND=1
	while getopts "i:s:" arg
	do
		case $arg in
            s) # session token
                s="$OPTARG"
                ;;
			i) # BACKUP SET ID
				bid="$OPTARG"
				;;
			*)
				return 1
				;;
		esac
	done

	mage_query -s $s -q "scm/is/${bid}/archive" >/dev/null
	return $?
}

function mage_latest_backup_age
{
	typeset cid arg ok s
	OPTIND=1
	while getopts "i:s:" arg
	do
		case $arg in
            s) # session token
                s="$OPTARG"
                ;;
			i) # COMPONENT INSTANCE ID
				cid="$OPTARG"
				;;
			*)
				return 1
				;;
		esac
	done

	mage_query -q "scm/bck/latest/ci/${cid}/age" -s $s
	return $?
}

function mage_url
{
    typeset query s arg
    OPTIND=1
    while getopts "q:" arg
    do
        case ${arg} in
            q) # HTTP query. If relative, will be appended to $MAGE_BASE_URL
                query="$OPTARG"
                ;;
            *)
                return 1
                ;;
        esac
    done

    ## Full or not? Happens for files which may be hosted on another server than base url.
    if [[ ${query:0:4} != "http" ]]
    then
        if [[ ${query:0:1} == "/" ]]
        then
            query="${MAGE_BASE_URL}${query}"
        else
            query="${MAGE_BASE_URL}/${query}"
        fi
    fi
    
    echo $query
}