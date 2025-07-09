# Dynamic Pricing and Date Management System for F.A.C.T.S Website

## Overview

I've implemented a comprehensive dynamic content management system that automatically links all pricing, dates, and content throughout your website. This means you can change values in one place (the admin panel) and they will update across all pages automatically.

## Key Features

### 1. **Dynamic Pricing System**
- All pricing information is stored in the database and automatically calculated
- Regular price: $2,200 AUD
- Early bird price: $1,650 AUD  
- Savings amount: $550 AUD (automatically calculated)
- Currency can be changed globally
- All pricing displays consistently across all pages

### 2. **Dynamic Date Management**
- Session start date: August 6, 2025
- Early bird deadline: July 31, 2025 (11:59 PM)
- Countdown timers automatically use the deadline from database
- Session days and times are configurable
- All date references update automatically

### 3. **Dynamic Content Templates**
- Text templates with placeholders like `{savings}`, `{deadline}`, `{spots}`
- Early bird banner automatically shows current values
- Content can be updated without touching code

### 4. **Admin Interface**
- Easy-to-use settings panel at `/admin/settings`
- Organized by categories: Pricing, Dates, Content, General
- Real-time preview of changes
- Reset to defaults option

## How It Works

### Database Structure
The `SiteSetting` model stores all configurable values:
- `key`: Setting name (e.g., 'regular_price')
- `value`: The actual value
- `value_type`: 'text', 'number', 'date', 'datetime', 'boolean'
- `description`: Help text for admins
- `category`: Groups related settings

### Template Integration
Templates now use dynamic values instead of hardcoded ones:

**Before:**
```html
<p>Save $550 if you enroll by July 31, 2025</p>
<div class="price">$2,200 <span>AUD</span></div>
```

**After:**
```html
<p>{{ get_dynamic_text(site_settings.home_early_bird_banner_template) }}</p>
<div class="price">{{ site_settings.regular_price|format_currency }} <span>{{ site_settings.currency }}</span></div>
```

### Automatic Calculations
The system automatically computes:
- Savings amount (regular_price - early_bird_price)
- Countdown timer deadline formatting
- Date displays in various formats
- Dynamic text replacement

## Files Modified

### Core System Files:
1. **`init_site_settings.py`** - Initializes all default settings
2. **`app.py`** - Added template filters, context processor, admin routes
3. **`models.py`** - SiteSetting model (already existed)

### Templates Updated:
1. **`templates/index.html`** - Homepage dynamic pricing and dates
2. **`templates/pricing.html`** - Pricing page dynamic values
3. **`templates/admin/settings.html`** - Admin settings interface

### New Features Added:
- Template filters: `format_currency`, `format_date`, `format_datetime`
- Dynamic text function: `get_dynamic_text()`
- Computed values: savings calculations, formatted dates
- Admin routes: settings management, reset functionality

## How to Use

### 1. Access Admin Settings
- Go to `/admin/login` (temporary auto-login enabled)
- Navigate to "Settings" in the admin panel
- Or visit `/admin/settings` directly

### 2. Update Pricing
To change the course price:
1. Update `regular_price` (e.g., change from 2200 to 2500)
2. Update `early_bird_price` (e.g., change from 1650 to 1950)
3. The savings amount will automatically calculate (550 in this example)
4. All pages will show the new pricing immediately

### 3. Update Dates
To change session dates:
1. Update `next_session_start_date` (e.g., 2025-09-15)
2. Update `early_bird_deadline` (e.g., 2025-08-31 23:59:59)
3. All countdown timers and date displays will update automatically

### 4. Customize Content
To change text across the site:
1. Update any content setting (e.g., `home_hero_title`)
2. Use placeholders in templates like `{savings}`, `{deadline}`, `{spots}`
3. The system will replace placeholders with current values

## Examples of Dynamic Content

### Dynamic Early Bird Banner
Template: `🎉 Save ${savings} if you enroll by {deadline} – Only {spots} seats per session!`
Output: `🎉 Save $550 if you enroll by July 31 – Only 10 seats per session!`

### Dynamic Pricing Display
```html
Regular Price: $2,200 AUD
Early Bird Price: $1,650 AUD
You Save: $550 AUD
```

### Dynamic Countdown Timer
JavaScript automatically uses: `July 31, 2025 23:59:59`

## Benefits

1. **Consistency**: All pricing and dates are synchronized across the website
2. **Easy Updates**: Change values in one place, update entire site
3. **No Code Changes**: Admin can update content without developer
4. **Automatic Calculations**: Savings amounts and percentages calculated automatically
5. **Error Prevention**: No more forgetting to update a page when prices change
6. **Professional**: Always shows current, accurate information

## Technical Notes

### Placeholders Available:
- `{savings}` - Early bird savings amount
- `{deadline}` - Early bird deadline (formatted)
- `{spots}` - Maximum class size
- `{regular_price}` - Regular course price
- `{early_bird_price}` - Early bird price
- `{currency}` - Currency code

### Template Filters:
- `|format_currency` - Formats numbers as currency ($2,200)
- `|format_date` - Formats dates (August 6, 2025)
- `|format_datetime` - Formats date/time with time

### Computed Values Available in Templates:
- `computed.savings_amount` - Calculated savings
- `computed.early_bird_deadline_js` - JS-formatted deadline
- `computed.early_bird_deadline_display` - Human-readable deadline
- `computed.session_start_formatted` - Formatted session start date

## Future Enhancements

The system is designed to be easily extensible. You can add new settings for:
- Multiple course offerings
- Regional pricing
- Seasonal promotions
- A/B testing different messages
- Multi-language support

## Testing the System

1. Visit the website homepage
2. Note the current pricing and dates
3. Go to `/admin/settings`
4. Change the `regular_price` from 2200 to 2500
5. Save changes
6. Return to homepage - pricing should update automatically
7. Change `early_bird_deadline` to a different date
8. Verify countdown timer updates

The system is now live and all your pricing and date information is fully dynamic and centralized!
