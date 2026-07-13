#!/usr/bin/env bash
set -u

RTL_FILE="${1:-examples/sync_fifo/sync_fifo.sv}"
TB_FILE="${2:-examples/sync_fifo/sync_fifo_tb.sv}"
STATUS=0
RAN_EDA=0

pass() {
  printf 'PASS %-18s %s\n' "$1" "$2"
}

fail() {
  printf 'FAIL %-18s %s\n' "$1" "$2"
  STATUS=1
}

skip() {
  printf 'SKIP %-18s %s\n' "$1" "$2"
}

rtl_without_line_comments() {
  sed 's,//.*$,,' "$RTL_FILE"
}

run_static_checks() {
  if [ ! -f "$RTL_FILE" ]; then
    fail "static" "missing $RTL_FILE"
    return
  fi
  if [ ! -f "$TB_FILE" ]; then
    fail "static" "missing $TB_FILE"
    return
  fi

  grep -Eq 'module[[:space:]]+sync_fifo' "$RTL_FILE" \
    && pass "static" "sync_fifo module exists" \
    || fail "static" "sync_fifo module declaration not found"

  for signal in clk rst_n wr_en rd_en din dout full empty; do
    grep -Eq "\\b${signal}\\b" "$RTL_FILE" \
      && pass "static" "port/signal ${signal} found" \
      || fail "static" "port/signal ${signal} missing"
  done

  if grep -Eq 'TODO|intentionally incomplete' "$RTL_FILE"; then
    fail "static" "starter TODO remains in RTL"
  else
    pass "static" "no starter TODO marker"
  fi

  if grep -Eq 'intended|profile available|not needed' "$RTL_FILE"; then
    fail "static" "RTL contains non-evidence model-routing claim"
  else
    pass "static" "no model-routing claim embedded in RTL"
  fi

  if rtl_without_line_comments | grep -Eq '\bDEPTH[[:space:]]*\['; then
    fail "static" "parameter DEPTH is indexed like a vector"
  else
    pass "static" "no DEPTH vector indexing"
  fi

  rtl_without_line_comments | grep -Eq 'always_ff|always[[:space:]]*@' \
    && pass "static" "sequential logic block found" \
    || fail "static" "no sequential logic block found"

  rtl_without_line_comments | grep -Eq '(^|[^A-Za-z0-9_])(mem|storage|ram)([^A-Za-z0-9_]|$)|logic[[:space:]].*\[[^]]+\].*[A-Za-z_][A-Za-z0-9_]*[[:space:]]*\[[^]]+\]' \
    && pass "static" "storage declaration likely present" \
    || fail "static" "no storage declaration found"

  rtl_without_line_comments | grep -Eq 'count|occupancy|used' \
    && pass "static" "occupancy/count logic likely present" \
    || fail "static" "no occupancy/count logic found"
}

run_verilator() {
  if command -v verilator >/dev/null 2>&1; then
    RAN_EDA=1
    if verilator --lint-only -Wall "$RTL_FILE"; then
      pass "verilator" "lint passed"
    else
      fail "verilator" "lint failed"
    fi
  else
    skip "verilator" "tool not installed"
  fi
}

run_iverilog() {
  if command -v iverilog >/dev/null 2>&1 && command -v vvp >/dev/null 2>&1; then
    RAN_EDA=1
    OUT="${TMPDIR:-/tmp}/sync_fifo_tb.vvp"
    if iverilog -g2012 -o "$OUT" "$RTL_FILE" "$TB_FILE" && vvp "$OUT"; then
      pass "iverilog" "simulation passed"
    else
      fail "iverilog" "simulation failed"
    fi
  else
    skip "iverilog" "tool not installed"
  fi
}

run_yosys() {
  if command -v yosys >/dev/null 2>&1; then
    RAN_EDA=1
    if yosys -q -p "read_verilog -sv $RTL_FILE; synth -top sync_fifo"; then
      pass "yosys" "synthesis check passed"
    else
      fail "yosys" "synthesis check failed"
    fi
  else
    skip "yosys" "tool not installed"
  fi
}

echo "RTL validation target:"
echo "  RTL: $RTL_FILE"
echo "  TB:  $TB_FILE"

run_static_checks
run_verilator
run_iverilog
run_yosys

if [ "$RAN_EDA" -eq 0 ]; then
  echo "NOTE no EDA tools were installed; result is static-only."
fi

exit "$STATUS"
