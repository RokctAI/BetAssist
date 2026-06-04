import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:core_sdk/core_sdk.dart';

class BudgetSelectorWidget extends StatefulWidget {
  final double initialBudget;
  final ValueChanged<double> onBudgetSelected;

  const BudgetSelectorWidget({
    super.key,
    required this.initialBudget,
    required this.onBudgetSelected,
  });

  @override
  State<BudgetSelectorWidget> createState() => _BudgetSelectorWidgetState();
}

class _BudgetSelectorWidgetState extends State<BudgetSelectorWidget> {
  double _budget = 0;

  @override
  void initState() {
    super.initState();
    _budget = widget.initialBudget;
  }

  @override
  Widget build(BuildContext context) {
    final singleBetCap = _budget * 0.02;

    return Column(
      mainAxisSize: MainAxisSize.min,
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Responsible Play Budget',
          style: AppStyle.interBold(
            color: AppStyle.white,
            size: 24,
          ),
        ),
        SizedBox(height: 8.h),
        Text(
          'Set your maximum monthly limit. The 2% risk rule limits single stakes automatically.',
          style: AppStyle.interNormal(
            color: AppStyle.white.withOpacity(0.6),
            size: 14,
          ),
        ),
        SizedBox(height: 32.h),
        Center(
          child: Column(
            children: [
              Text(
                'R ${_budget.toInt()}',
                style: AppStyle.interBold(
                  color: AppStyle.primary,
                  size: 48,
                ),
              ),
              Text(
                'Monthly Stake Limit',
                style: AppStyle.interNormal(
                  color: AppStyle.white.withOpacity(0.5),
                  size: 14,
                ),
              ),
            ],
          ),
        ),
        SizedBox(height: 24.h),
        SliderTheme(
          data: SliderThemeData(
            activeTrackColor: AppStyle.primary,
            inactiveTrackColor: Colors.white10,
            thumbColor: AppStyle.primary,
            overlayColor: AppStyle.primary.withOpacity(0.2),
            valueIndicatorColor: AppStyle.primary,
          ),
          child: Slider(
            min: 500,
            max: 10000,
            divisions: 19,
            label: 'R ${_budget.toInt()}',
            value: _budget < 500 ? 500 : (_budget > 10000 ? 10000 : _budget),
            onChanged: (val) {
              setState(() {
                _budget = val;
              });
              widget.onBudgetSelected(val);
            },
          ),
        ),
        SizedBox(height: 24.h),
        Container(
          padding: EdgeInsets.all(16.w),
          decoration: BoxDecoration(
            color: Colors.white.withOpacity(0.03),
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: Colors.white10),
          ),
          child: Row(
            children: [
              Icon(Icons.shield_outlined, color: AppStyle.primary, size: 24.sp),
              SizedBox(width: 12.w),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Max Stake Per Bet: R ${singleBetCap.toInt()}',
                      style: AppStyle.interSemi(
                        color: AppStyle.white,
                        size: 14,
                      ),
                    ),
                    Text(
                      'Protected by the 2% maximum exposure policy.',
                      style: AppStyle.interNormal(
                        color: AppStyle.white.withOpacity(0.5),
                        size: 12,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }
}
