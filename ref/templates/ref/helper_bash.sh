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
		echo "an error occured - HTTP code $http_code - WGET code $ok - Query was ${MAGE_BASE_URL}/$query" >&2		
		return $http_code
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
		echo "ERROR" -m "Error in MAGE connection" >&2
		return $ok
	fi
	printf "$res" | grep "200 OK" 2>&1 >/dev/null
	if [[ $? -ne 0 ]]
	then
		echo "an error occurred during MAGE login.\n$res" >&2
		return 1
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
		echo "session does not exist" >&2
		return 1
	fi
    
	mage_query -q "accounts/scriptlogout" -s $ss >/dev/null
	ok=$?
	if [[ $ok -ne 0 ]]
	then
		echo "WARNING - Error in MAGE logout" >&2		
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
		echo "ERROR  Error in MAGE MCL query\n$query" >&2
        cat $tmpFile >&2
        rm -f $tmpFile
		return $ok
	fi
    
	. $tmpFile
    rm -f $tmpFile  
    
    if [[ ${MAGE_RESULT_COUNT} -eq 0 ]] && [[ $u -eq 1 ]]
    then    
        echo "Query awaited a single result but there were none returned" >&2
        return 3
    elif [[ ${MAGE_RESULT_COUNT} -gt 0 ]] && [[ $u -eq 1 ]]
    then
        echo "Query awaited a single result but there were more" >&2
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
        echo "an argument name must be given" >&2
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
            echo "Result $i has no field named $a"
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
        echo "delivery name must be specified" >&200
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
			i) # set ID or name
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
    
	. $resFile
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

function mage_test_ii_dependencies_full
{
    typeset arg ii s e ok res
	OPTIND=1
	while getopts "s:i:e:" arg
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
			*)
				return 1
				;;
		esac
	done
    
	res=$(mage_query -s $s -q "scm/ii/$ii/testonenvtscriptfull/$e")
	# note that only very recent wget have --content-on-error option. So this will not display the failed dependency.
    return $?
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
