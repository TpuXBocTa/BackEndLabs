#!/usr/bin/env bash
set -euo pipefail


retries=12
until flask --app lab2_app db upgrade >/dev/null 2>&1 || [ $retries -le 0 ]; do
  echo "wait for db"
  retries=$((retries-1))
  sleep 2
done


echo "Strat migration..."
flask --app lab2_app db upgrade

if [ "${ADD_TEST_DATA:-0}" = "1" ]; then
  echo "Seeding..."
  flask --app lab2_app test_data
fi


exec flask --app lab2_app run --host=0.0.0.0 --port=8000