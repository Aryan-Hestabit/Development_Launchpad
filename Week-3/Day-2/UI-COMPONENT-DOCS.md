# UI Components Documentation

This document provides documentation for the UI components located in the `components/ui/` directory.

## Badge

A badge component for displaying status indicators or labels.

### Props

- `children`: The content to display inside the badge.
- `type` (optional): The type of badge. Options: `"default"`, `"critical"`, `"success"`, `"pending"`. Default: `"default"`.
- `color` (optional): A custom color for the badge. If provided, it overrides the `type` styling.

### Usage

```jsx
import Badge from './components/ui/Badge';

// Default badge
<Badge>Default</Badge>

// Status badges
<Badge type="success">Success</Badge>
<Badge type="critical">Critical</Badge>
<Badge type="pending">Pending</Badge>

// Custom color badge
<Badge color="blue">Custom Blue</Badge>
```

## Button

A customizable button component with different styles.

### Props

- `children`: The content to display inside the button.
- `style` (optional): The style variant. Options: `"1"` (blue), `"2"` (gray), `"3"` (red), `"4"` (full-width blue). Default: `"1"`.
- `onClick` (optional): Click handler function.
- `type` (optional): The button type. Default: `"button"`.

### Usage

```jsx
import Button from './components/ui/Button';

// Default blue button
<Button onClick={handleClick}>Click Me</Button>

// Different styles
<Button style="2">Gray Button</Button>
<Button style="3">Red Button</Button>
<Button style="4">Full Width Button</Button>
```

## Card (FeatureCard)

A simple card component for displaying features or content.

### Props

- `title`: The title to display in the card.
- `description`: The description text to display in the card.

### Usage

```jsx
import FeatureCard from './components/ui/Card';

<FeatureCard
  title="Feature Title"
  description="This is a description of the feature."
/>
```

## Input

A versatile input component supporting various input types.

### Props

- `label` (optional): The label for the input.
- `type` (optional): The input type. Options: `"text"`, `"email"`, `"password"`, `"search"`, `"number"`, `"date"`, `"file"`, `"textarea"`. Default: `"text"`.
- `placeholder` (optional): Placeholder text. If not provided, defaults are used based on type.
- `value` (optional): The value of the input.
- `onChange` (optional): Change handler function.
- `name` (optional): The name attribute for the input.
- `rows` (optional): Number of rows for textarea. Default: `4`.
- Other props are spread to the input/textarea element.

### Usage

```jsx
import Input from './components/ui/Input';

// Text input
<Input type="text" placeholder="Enter your name" />

// Email input
<Input type="email" />

// Password input
<Input type="password" />

// Search input
<Input type="search" />

// Number input
<Input type="number" />

// Date input
<Input type="date" />

// File input
<Input type="file" />

// Textarea
<Input type="textarea" rows={6} />
```
